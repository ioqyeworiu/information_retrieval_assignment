import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVectorStore

class EmbeddingModel:
    def __init__(self, collection_name="fitness_coach_embeddings"):
        self.model_name = os.getenv("=EMBEDDING_MODEL_NAME2")
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
        self.vector_store = PGVectorStore(connection=os.getenv("db_connection_string"), collection_name=collection_name, embeddings=self.embeddings)
    
    def add_documents(self, documents):
        ids = [doc.metadata["id"] for doc in documents]
        self.vector_store.add_documents(documents, ids=ids, metadatas=[doc.metadata for doc in documents])
        return True
    
    def get_retriever(self, search_type="similarity", k=4):
        return self.vector_store.as_retriever(search_type=search_type, k=k)