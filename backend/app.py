from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag.retriever import Retriever
from llm.llm_client import generate_answer
import pickle

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


with open("embeddings.pkl", "rb") as f:
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
