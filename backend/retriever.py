import numpy as np


class Retriever:
    def __init__(self, embeddings, documents):
        self.embeddings = np.array(embeddings)
        self.documents = documents

    def search(self, query: str, k: int = 5):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_vec = model.encode([query])[0]
        scores = self.embeddings @ query_vec / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_vec) + 1e-10
        )
        top_k = np.argsort(scores)[::-1][:k]
        return [self.documents[i] for i in top_k]
