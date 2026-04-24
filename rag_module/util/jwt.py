from fastapi.security import HTTPBearer
import jwt
from datetime import datetime, timedelta, timezone
from rag_module.dto.user_dto import UserDTO
from fastapi import Depends, HTTPException, status
from dotenv import load_dotenv
import os

load_dotenv(override=True)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
security = HTTPBearer()

def create_access_token(user_dto: UserDTO):
    payload = {
        "sub": str(user_dto.id),
        "claims": {
            "username": user_dto.username,
            "role": "user",
        },
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(timezone.utc)
    }

    token = jwt.encode(
        payload,
        key=JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token

def get_credentials(credentials = Depends(security)):
    try:
        payload = jwt.decode(
            jwt = credentials.credentials,
            key=JWT_SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")