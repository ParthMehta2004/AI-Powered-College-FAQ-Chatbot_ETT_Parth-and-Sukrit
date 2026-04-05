import faiss
import numpy as np

model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

class Retriever:
    def __init__(self, embeddings, documents):
        self.documents = documents
        emb_array = np.array(embeddings).astype('float32')
        self.index = faiss.IndexFlatL2(emb_array.shape[1])
        self.index.add(emb_array)

    def search(self, query, k=5):
        model = get_model()
        query_vector = model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_vector, k)
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]
