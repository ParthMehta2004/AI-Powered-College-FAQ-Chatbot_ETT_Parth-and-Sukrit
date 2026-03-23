from fastapi import FastAPI
from rag.loader import extract_text_from_pdf
from rag.embedder import chunk_text, generate_embeddings
from rag.retriever import Retriever
from llm.llm_client import generate_answer
from visualization.logger import log_query
import os

app = FastAPI()


documents = []
for file in os.listdir("data/raw"):
    if file.endswith(".pdf"):
        text = extract_text_from_pdf(os.path.join("data/raw", file))
        documents.append(text)

# Chunking
chunks = []
for doc in documents:
    chunks.extend(chunk_text(doc))


embeddings = generate_embeddings(chunks)


retriever = Retriever(embeddings, chunks)


@app.get("/")
def home():
    return {"message": "College FAQ Chatbot Running"}

@app.post("/ask")
def ask(question: str):
    results = retriever.search(question)
    context = "\n".join(results)

    answer = generate_answer(context, question)


    log_query(question, answer)

    return {"answer": answer}
