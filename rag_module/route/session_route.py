from fastapi import Depends, Body, APIRouter
from fastapi.security import HTTPBearer
from rag_module.service.session_service import SessionService
from rag_module.util.jwt import get_credentials

session_router = APIRouter()

security = HTTPBearer()

class SessionRoute:

    @session_router.get(f"/api/public/v1/sessions")
    def get_sessions(credentials = Depends(get_credentials), session_service: SessionService = Depends(SessionService)):
        return {"data": session_service.get_sessions_by_user_id(credentials)}
    
    @session_router.get(f"/api/public/v1/sessions/{{session_id}}")
    def get_session(session_id: str, session_service: SessionService = Depends(SessionService)):
        return {"data": session_service.get_chat_by_session_id(session_id)}
    
    @session_router.post(f"/api/public/v1/sessions")
    def create_session(credentials = Depends(get_credentials), session_service: SessionService = Depends(SessionService)):
        return session_service.create_session(credentials)