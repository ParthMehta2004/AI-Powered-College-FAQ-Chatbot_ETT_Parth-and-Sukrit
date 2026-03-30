import os
import pickle
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from rag.retriever import Retriever
from llm.llm_client import generate_answer

# Global retriever - loaded after server starts
retriever = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy resources AFTER uvicorn binds to the port."""
    global retriever
    # embeddings.pkl is at the repo root (one level above backend/)
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
        retriever = None

    yield  # Server runs here

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
def ask(question: str = Query(..., description="The question to ask the chatbot")):
    """Answer a college FAQ question using RAG."""
    if not question or not question.strip():
        return {"answer": "Please provide a valid question."}

    if retriever is None:
        return {"answer": "Server is still loading embeddings, please try again in a moment."}

    try:
        results = retriever.search(question)
        context = "\n".join(results)
        answer = generate_answer(context, question)
        return {"answer": answer}
    except Exception as e:
        print(f"=== ERROR in /ask: {e} ===", flush=True)
        return {"answer": f"An error occurred while processing your question: {str(e)}"}
