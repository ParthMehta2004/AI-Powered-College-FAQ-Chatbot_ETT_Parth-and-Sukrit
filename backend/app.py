import os
import pickle
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag.retriever import Retriever
from llm.llm_client import generate_answer

app = FastAPI()

# CORS (needed for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve embeddings.pkl path relative to repo root (works regardless of CWD)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings.pkl")

if not os.path.exists(EMBEDDINGS_PATH):
    raise FileNotFoundError(f"embeddings.pkl not found at {EMBEDDINGS_PATH}")

with open(EMBEDDINGS_PATH, "rb") as f:
    chunks, embeddings = pickle.load(f)

retriever = Retriever(embeddings, chunks)

@app.get("/")
def home():
    return {"message": "Chatbot running"}

@app.post("/ask")
def ask(question: str):
    results = retriever.search(question)
    context = "\n".join(results)
    answer = generate_answer(context, question)
    return {"answer": answer}
