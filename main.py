import os
import pickle
import asyncio
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from rag.retriever import Retriever
from api.llm_client import generate_answer

retriever = None
is_ready = False

def load_embeddings():
    global retriever, is_ready
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(BASE_DIR, "embeddings.pkl")
        print(f"Loading embeddings from {path}", flush=True)
        with open(path, "rb") as f:
            chunks, embeddings = pickle.load(f)
        retriever = Retriever(embeddings, chunks)
        is_ready = True
        print(f"Ready: {len(chunks)} chunks loaded", flush=True)
    except Exception as e:
        print(f"ERROR loading embeddings: {e}", flush=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=load_embeddings, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "status": "loaded" if is_ready else "loading..."}

@app.post("/ask")
async def ask(question: str = Query(...)):
    if not question.strip():
        return {"answer": "Please ask a question."}
    if not is_ready:
        return {"answer": "Still loading knowledge base, please try again in 20 seconds."}
    try:
        loop = asyncio.get_event_loop()
        results = retriever.search(question)
        context = "\n".join(results)
        answer = await asyncio.wait_for(
            loop.run_in_executor(None, generate_answer, context, question),
            timeout=30.0
        )
        return {"answer": answer}
    except asyncio.TimeoutError:
        return {"answer": "Request timed out. Please try again."}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

@app.get("/debug")
async def debug():
    api_key = os.getenv("GROQ_API_KEY")
    return {
        "groq_key_set": bool(api_key),
        "embeddings_loaded": is_ready,
        "chunks": len(retriever.documents) if retriever else 0
    }

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
