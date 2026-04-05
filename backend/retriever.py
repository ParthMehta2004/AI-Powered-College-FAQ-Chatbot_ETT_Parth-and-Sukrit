import numpy as np
import faiss

_model = None

def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _model

class Retriever:
    def __init__(self, embeddings, documents):
        self.documents = documents
        arr = np.array(embeddings, dtype="float32")
        self.index = faiss.IndexFlatL2(arr.shape[1])
        self.index.add(arr)

    def search(self, query: str, k: int = 5):
        model = _get_model()
        vec = np.array(list(model.embed([query])), dtype="float32")
        _, indices = self.index.search(vec, k)
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]
