import os
import pickle
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag.retriever import Retriever
from llm.llm_client import generate_answer

# Global retriever - loaded after server starts
retriever = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load heavy resources AFTER uvicorn binds to the port."""
    global retriever
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings.pkl")
    with open(EMBEDDINGS_PATH, "rb") as f:
        chunks, embeddings = pickle.load(f)
    retriever = Retriever(embeddings, chunks)
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
    return {"message": "Chatbot running"}

@app.post("/ask")
def ask(question: str):
    if retriever is None:
        return {"answer": "Server is still loading, please try again in a moment."}
    results = retriever.search(question)
    context = "\n".join(results)
    answer = generate_answer(context, question)
    return {"answer": answer}
