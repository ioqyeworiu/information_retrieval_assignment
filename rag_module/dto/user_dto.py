from pydantic import BaseModel, Field

class UserDTO(BaseModel):
    id: int | None = Field(required=False, default=None)
    username: str = Field(required=False)
    email: str = Field(required=False, default=None)
    password: str = Field(required=False)
    full_name: str = Field(default=None)
    birth: str = Field(default=None)
    gender: str = Field(default=None)
    height: int | None = Field(default=None)
    weight: int | None = Field(default=None)
    goal: str | None = Field(default=None)
    exercise_favourite: str | None = Field(default=None)
    diet_favourite: str | None = Field(default=None)
    practice_plan: str | None = Field(default=None)