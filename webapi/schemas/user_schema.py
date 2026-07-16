from typing import List, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .prompt_schema import PromptRead


class UserCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "usertest",
                "name": "user",
                "last_name": "testing",
                "email": "user@example.com",
                "password": "usertest",
                "preferred_language": "es",
            }
        },
    )

    username: str = Field(max_length=50)
    name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    password: str = Field(max_length=255)
    preferred_language: Literal["es", "en"] = "es"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    last_name: str
    email: str
    preferred_language: str
    role: str

class UserReadWithPrompts(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    last_name: str
    email: str
    preferred_language: str
    role: str
    prompts: List[PromptRead] = []
