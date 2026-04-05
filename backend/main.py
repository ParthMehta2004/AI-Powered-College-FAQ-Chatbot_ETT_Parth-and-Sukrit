import os
import pickle
import asyncio
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

retriever = None
is_ready = False


def load():
    global retriever, is_ready
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        pkl = os.path.join(base, "embeddings.pkl")
        print(f"startup: loading {pkl}", flush=True)
        with open(pkl, "rb") as f:
            chunks, embeddings = pickle.load(f)
        from retriever import Retriever
        retriever = Retriever(embeddings, chunks)
        is_ready = True
        print(f"startup: ready {len(chunks)} chunks", flush=True)
    except Exception as e:
        print(f"startup: ERROR {e}", flush=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=load, daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True, "status": "loaded" if is_ready else "loading"}


@app.post("/ask")
async def ask(question: str = Query(...)):
    if not question.strip():
        return {"answer": "Please ask a question."}
    if not is_ready:
        return {"answer": "Still loading knowledge base, please wait 20 seconds and try again."}
    try:
        from llm_client import generate_answer
        loop = asyncio.get_event_loop()
        results = retriever.search(question, k=5)
        context = "\n".join(results)
        answer = await asyncio.wait_for(
            loop.run_in_executor(None, generate_answer, context, question),
            timeout=30.0,
        )
        return {"answer": answer}
    except asyncio.TimeoutError:
        return {"answer": "Request timed out. Please try again."}
    except Exception as e:
        return {"answer": f"Server error: {e}"}


@app.get("/debug")
def debug():
    key = os.getenv("GROQ_API_KEY", "")
    return {
        "groq_key_set": bool(key),
        "embeddings_loaded": is_ready,
        "chunks": len(retriever.documents) if retriever else 0,
    }
