import email

from rag_module.util.database import Session_local
from rag_module.model.user import User


class UserRepository:
    def __init__(self):
        self.db = Session_local()
    
    def save_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()