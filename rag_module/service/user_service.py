from passlib.hash import bcrypt
from rag_module.dto.user_dto import UserDTO
from rag_module.model.user import User
from fastapi import Depends, HTTPException
from rag_module.util.jwt import create_access_token
from rag_module.repository.user_repository import UserRepository
from rag_module.repository.session_repository import SessionRepository

class UserService:

    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        session_repository: SessionRepository = Depends(SessionRepository),
    ):
        self.userRepository = user_repository
        self.sessionRepository = session_repository
    
    def create_user(self, user_dto):
        user = User()
        user.username = user_dto.username
        user.email = user_dto.email
        user.password = bcrypt.hash(user_dto.password)
        user.full_name = user_dto.full_name
        user.birth = user_dto.birth
        user.gender = user_dto.gender
        user.height = user_dto.height
        user.weight = user_dto.weight
        user.goal = user_dto.goal
        user.excercise_favourite = user_dto.exercise_favourite
        user.diet_favourite = user_dto.diet_favourite
        user.practice_plan = user_dto.practice_plan
        self.userRepository.save_user(user)

        self.sessionRepository.create_session(user)
        return True
    
    def get_current_user(self, user_id: int):
        user = self.userRepository.get_user_by_id(user_id)
        user_dto = UserDTO()
        user_dto.id = user.id
        user_dto.username = user.username
        user_dto.email = user.email
        user_dto.full_name = user.full_name
        user_dto.birth = user.birth
        user_dto.gender = user.gender
        user_dto.height = user.height
        user_dto.weight = user.weight
        user_dto.goal = user.goal
        user_dto.exercise_favourite = user.exercise_favourite
        user_dto.diet_favourite = user.diet_favourite
        user_dto.practice_plan = user.practice_plan
        return user_dto

    def login_user(self, user_dto):
        user_db = self.userRepository.get_user_by_username(user_dto.username)
        if bcrypt.verify(user_dto.password, user_db.password):
            user_dto.id = user_db.id
            #return jwt
            token = create_access_token(user_dto)
            return token
        raise HTTPException(status_code=401, detail="Invalid username or password")