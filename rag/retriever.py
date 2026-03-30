import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load model once at module level (lazy, but cached across requests)
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
    return _model

class Retriever:
    def __init__(self, embeddings, documents):
        self.documents = documents
        self.index = faiss.IndexFlatL2(len(embeddings[0]))
        self.index.add(np.array(embeddings))

    def search(self, query, k=3):
        model = get_model()
        query_vector = model.encode([query])
        distances, indices = self.index.search(query_vector, k)
        return [self.documents[i] for i in indices[0]]
