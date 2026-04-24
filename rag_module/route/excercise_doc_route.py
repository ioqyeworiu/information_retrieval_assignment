from fastapi.security import HTTPBearer

from rag_module.service.excercise_doc_service import ExerciseDocService
from fastapi import APIRouter, Depends, Body, Query
from fastapi.security import HTTPBearer
from rag_module.util.jwt import get_credentials

exercise_doc_router = APIRouter()

security = HTTPBearer()

class ExerciseDocRoute:

    @exercise_doc_router.get(f"/api/public/v1/excercise_docs/{{exercise_doc_id}}")
    def get_exercise_doc_by_id(exercise_doc_id: int, exercise_doc_service: ExerciseDocService = Depends()):
        return exercise_doc_service.get_exercise_doc_by_id(exercise_doc_id)

    @exercise_doc_router.post(f"/api/public/v1/excercise_docs")
    def get_exercise_doc(credentials: int = Depends(get_credentials), query_n: int = Query(default=21), query: str = Body(), exercise_doc_service: ExerciseDocService = Depends()):
        return {"data": exercise_doc_service.get_exercise_doc(credentials, query_n, query)}