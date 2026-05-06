import json

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from langchain_postgres import PGVector
from rag_module.route.answer_route import answer_router
from rag_module.route.excercise_doc_route import exercise_doc_router
from rag_module.route.user_route import user_router
from rag_module.route.session_route import session_router
from rag_module.model.user_excercise_doc import UserExerciseDoc
from langchain_huggingface import HuggingFaceEmbeddings
from uvicorn import run
from rag_module import model
from tf_idf_module.tf_idf_vectorizer import TFIDFVectorizer
from similarity_module.okapi_bm25 import Bm25Okapi
from rag_module.util.database import engine, Model
from dotenv import load_dotenv
import os

load_dotenv(override=True)

DB_URI = os.getenv("db_connection_string")
COLLECTION_1 = os.getenv("vector_collection_name")
COLLECTION_2 = COLLECTION_1

def create_db_tables():
    Model.metadata.create_all(bind=engine)

def get_documents(path: str = "data/Knowedge_base_RAG/exercises/exercises/exercises_vn.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    return [(d["id"], d["instructions"]["vi"]) for d in data]

async def lifespan(app: FastAPI):
    create_db_tables()
    app.state.embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL_NAME2"))
    app.state.vector_store_1 = PGVector(
            connection=DB_URI,
            collection_name=COLLECTION_1,
            embeddings=app.state.embeddings,
        )
    app.state.vector_store_2 = PGVector(
            connection=DB_URI,
            collection_name=COLLECTION_2,
            embeddings=app.state.embeddings,
        )
    app.state.documents = get_documents()
    app.state.tf_idf_vectorizer = TFIDFVectorizer()
    app.state.tf_idf_vectorizer.fit(app.state.documents)
    app.state.bm25 = Bm25Okapi()
    app.state.bm25.fit(app.state.documents)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(answer_router)
app.include_router(exercise_doc_router)
app.include_router(user_router)
app.include_router(session_router)

app.mount(
    "/media",
    StaticFiles(directory="data/Knowedge_base_RAG/exercises"),
    name="media"
)

if __name__ == "__main__":
    run(app, host="localhost", port=8000)