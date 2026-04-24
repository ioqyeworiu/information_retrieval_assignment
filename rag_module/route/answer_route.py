from fastapi import Depends, Body, APIRouter
from rag_module.service.answer_service import AnswerService
from fastapi import Request
from fastapi.security import HTTPBearer
from rag_module.util.jwt import get_credentials

answer_router = APIRouter()
security = HTTPBearer()

class AnswerRoute:

    # @answer_router.post(f"/api/public/v1/answers/{{session_id}}/chat")
    # def get_answer(session_id: str, question: str = Body()):
    #     answer_service = AnswerService(session_id=session_id)
    #     return answer_service.get_answer(question)

    @answer_router.post(f"/api/public/v2/answers/{{session_id}}/chat")
    def get_answer_v2(session_id: str, request: Request, credentials = Depends(get_credentials), question: str = Body()):
        answer_service = AnswerService(session_id=session_id, request=request)
        return answer_service.get_answer_v2(credentials, question)