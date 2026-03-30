import faiss
import numpy as np

# Lazy module-level cache for the model
_model = None

def get_model():
    """Import SentenceTransformer lazily so it does NOT slow down uvicorn startup."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # deferred import
        _model = SentenceTransformer("all-MiniLM-L6-v2")  # must match embeddings.pkl
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
