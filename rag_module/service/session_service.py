from fastapi import Depends
import psycopg
from rag_module.dto.session_dto import SessionDTO
from rag_module.model.session import Session
from rag_module.repository.session_repository import SessionRepository
from rag_module.repository.user_repository import UserRepository
from langchain_postgres import PostgresChatMessageHistory
from uuid import uuid4
from dotenv import load_dotenv
import os

load_dotenv(override=True)


class SessionService:
    def __init__(self, session_repository: SessionRepository = Depends(SessionRepository), user_repository: UserRepository = Depends(UserRepository)):
        self.session_repository = session_repository
        self.user_repository = user_repository


    def create_session(self, user_id: int):
        session = Session()
        session.session_id = str(uuid4())
        session.user_id = user_id
        self.session_repository.save_session(session)
        return True
    
    def get_sessions_by_user_id(self, user_id: int):
        sessions = self.session_repository.get_sessions_by_user_id(user_id)
        return sessions
    
    def get_chat_by_session_id(self, session_id: str):
        connection = os.getenv("db_connection_string")
        sync_connection = psycopg.connect(connection)
        history = PostgresChatMessageHistory(
            os.getenv("historical_conversation_collection_name"),
            session_id,
            sync_connection=sync_connection
        )
        messages = history.get_messages()
        return messages