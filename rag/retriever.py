import faiss
import numpy as np
from rag.embedder import model

class Retriever:
    def __init__(self, embeddings, documents):
        self.documents = documents
        self.index = faiss.IndexFlatL2(len(embeddings[0]))
        self.index.add(np.array(embeddings))

    def search(self, query, k=3):
        query_vector = model.encode([query])
        distances, indices = self.index.search(query_vector, k)
        return [self.documents[i] for i in indices[0]]
