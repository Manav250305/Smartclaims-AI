import faiss
import numpy as np
from langchain_openai import OpenAIEmbeddings

class VectorStore:
    def __init__(self, chunks):
        self.embeddings = OpenAIEmbeddings()
        self.chunk_texts = chunks
        self.index = self.build_index()

    def build_index(self):
        vectors = self.embeddings.embed_documents(self.chunk_texts)
        dim = len(vectors[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(vectors).astype("float32"))
        return index

    def search(self, query, k=5):
        query_vec = self.embeddings.embed_query(query)
        D, I = self.index.search(np.array([query_vec]).astype("float32"), k)
        return [self.chunk_texts[i] for i in I[0]]