# Backend application entry point
from fastapi import FastAPI

app = FastAPI(title="College FAQ Chatbot")

@app.get("/")
def root():
    return {"message": "College FAQ Chatbot API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
