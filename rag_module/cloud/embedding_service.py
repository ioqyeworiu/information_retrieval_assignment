import modal
import os

app = modal.App("Embedding-service")
embedding_image = modal.Image.debian_slim().pip_install(
    "sentence-transformers", "huggingface_hub"
)

secret = modal.Secret.from_name("huggingface-secret")

volume = modal.Volume.from_name("embedding-service-cache", create_if_missing=True)

@app.cls(
    image=embedding_image,
    secrets=[secret],
    volumes={"/.cache": volume},
    gpu="T4",
    timeout=1800,
    max_containers=1,
    min_containers=0
)
class EmbeddingService:

    @modal.enter()
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer(os.getenv("EMBEDDING_MODEL_NAME2", "all-MiniLM-L6-v2"), cache_folder="/.cache")

    @modal.method()
    def get_embedding(self, text: str):
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()