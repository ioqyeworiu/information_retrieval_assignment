from fastapi import Depends, Request
from rag_module.repository.user_repository import UserRepository
from rag_module.repository.session_repository import SessionRepository
from rag_module.util.rag2 import RAGModel2


class AnswerService:
    def __init__(self, session_id, request: Request):
        self.session_id = session_id
        self.rag_model = RAGModel2(session_id=session_id, request=request)
        self.user_repository = UserRepository()
        self.session_repository = SessionRepository()

    # def get_answer(self, question):
    #     result = self.rag_model.ask(question)
    #     return result
    
    def get_answer_v2(self, credentials: int, question: str):
        session = self.session_repository.get_session_by_id(self.session_id)
        user = self.user_repository.get_user_by_id(credentials)
        if not session:
            session = self.session_repository.create_session(user)
        question += f"""
            User's full name: {user.full_name}
            User's goal: {user.goal}
            User's favourite: {user.excercise_favourite}
            User's diet favourite: {user.diet_favourite}
            User's birth: {user.birth}
            User's gender: {user.gender}
            User's practice plan: {user.practice_plan}
        """
        result = self.rag_model.get_chat_chain().invoke(
            {"input": question}
        )
        return result