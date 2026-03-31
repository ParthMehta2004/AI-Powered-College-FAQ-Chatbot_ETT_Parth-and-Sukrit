import os
import pickle
import asyncio
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from rag.retriever import Retriever
from llm.llm_client import generate_answer

retriever = None
is_ready = False

def load_everything():
    global retriever, is_ready
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings.pkl")
        print(f"=== [BG] Loading embeddings from: {EMBEDDINGS_PATH} ===", flush=True)
        with open(EMBEDDINGS_PATH, "rb") as f:
            chunks, embeddings = pickle.load(f)
        retriever = Retriever(embeddings, chunks)
        print(f"=== [BG] Embeddings loaded: {len(chunks)} chunks ===", flush=True)
        # NO pre-warming - skip it, it causes timeout
        is_ready = True
        print("=== [BG] Ready ===", flush=True)
    except Exception as e:
        print(f"=== [BG] ERROR: {e} ===", flush=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    t = threading.Thread(target=load_everything, daemon=True)
    t.start()
    yield  # port binds instantly

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
    return {"message": "Chatbot is running ✅", "status": "loaded" if is_ready else "loading"}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask")
async def ask(question: str = Query(...)):
    if not question or not question.strip():
        return {"answer": "Please provide a valid question."}
    if not is_ready:
        return {"answer": "Server is still warming up, please try again in 30 seconds."}
    try:
        loop = asyncio.get_event_loop()
        results = retriever.search(question)
        context = "\n".join(results)
        answer = await asyncio.wait_for(
            loop.run_in_executor(None, generate_answer, context, question),
            timeout=120.0
        )
        return {"answer": answer}
    except asyncio.TimeoutError:
        return {"answer": "Request timed out. Please try again."}
    except Exception as e:
        print(f"=== ERROR in /ask: {e} ===", flush=True)
        return {"answer": f"Error: {str(e)}"}

@app.get("/debug")
async def debug():
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY is NOT set"}
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "say hello in one word"}],
            max_tokens=10,
        )
        return {
            "status": "✅ Groq working",
            "response": response.choices[0].message.content,
            "retriever": "loaded" if is_ready else "still loading"
        }
    except Exception as e:
        return {"error": str(e)}
