from typing import List, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from core.password_policy import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    validate_password_strength,
)
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
                "password": "correct-horse-demo",
                "preferred_language": "es",
            }
        },
    )

    username: str = Field(max_length=50)
    name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    preferred_language: Literal["es", "en"] = "es"

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        return validate_password_strength(password)


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
