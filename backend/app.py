import os
import pickle
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from rag.retriever import Retriever
from llm.llm_client import generate_answer

retriever = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings.pkl")
    print(f"=== Loading embeddings from: {EMBEDDINGS_PATH} ===", flush=True)
    try:
        with open(EMBEDDINGS_PATH, "rb") as f:
            chunks, embeddings = pickle.load(f)
        retriever = Retriever(embeddings, chunks)
        print(f"=== Embeddings loaded: {len(chunks)} chunks ===", flush=True)
    except Exception as e:
        print(f"=== ERROR loading embeddings: {e} ===", flush=True)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Chatbot is running ✅", "status": "loaded" if retriever else "loading"}

@app.post("/ask")
async def ask(question: str = Query(...)):
    if not question or not question.strip():
        return {"answer": "Please provide a valid question."}
    if retriever is None:
        return {"answer": "Server is still loading, please try again in a moment."}
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
        print(f"=== ERROR in /ask: {e} ===", flush=True)
        return {"answer": f"Error: {str(e)}"}
