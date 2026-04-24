from pydantic import BaseModel, Field

class SessionDTO(BaseModel):
    session_id: str = Field(required=True)
    user_id: int = Field(required=True)