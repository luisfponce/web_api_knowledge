from typing import Optional

from core.prompt_options import MODEL_NAME_MAX_CHARS, is_valid_model_name
from models.prompts import PROMPT_TEXT_MAX_CHARS
from pydantic import BaseModel, Field, field_validator


class PromptCreate(BaseModel):
    user_id: Optional[int] = None
    title: str = Field(min_length=1, max_length=120)
    model_name: str = Field(min_length=1, max_length=MODEL_NAME_MAX_CHARS)
    prompt_text: str = Field(min_length=1, max_length=PROMPT_TEXT_MAX_CHARS)
    category: str
    rate: int = Field(ge=1, le=5)

    @field_validator("model_name", mode="before")
    @classmethod
    def strip_model_name(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        if not is_valid_model_name(value):
            raise ValueError("Unknown model_name")
        return value


class PromptRead(BaseModel):
    id: int
    user_id: int
    title: str
    model_name: str
    prompt_text: str
    category: str
    rate: int

    class Config:
        from_attributes = True
