from fastapi import APIRouter, Body, Depends
from fastapi.security import HTTPBearer
from rag_module.service.user_service import UserService
from rag_module.dto.user_dto import UserDTO
from rag_module.util.jwt import get_credentials

user_router = APIRouter()

security = HTTPBearer()

@user_router.get(f"/api/public/v1/users")
def get_current_user(
    credentials=Depends(get_credentials),
    user_service: UserService = Depends(UserService),
):
    return user_service.get_current_user(credentials)


@user_router.post(f"/api/public/v1/users/register")
def register_user(
    user_dto: UserDTO = Body(),
    user_service: UserService = Depends(UserService),
):
    return user_service.create_user(user_dto)


@user_router.post(f"/api/public/v1/users/login")
def login_user(
    user_dto: UserDTO = Body(),
    user_service: UserService = Depends(UserService),
):
    return {"jwt": user_service.login_user(user_dto)}