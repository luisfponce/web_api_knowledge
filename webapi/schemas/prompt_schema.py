from typing import Optional

from pydantic import BaseModel, Field


class PromptCreate(BaseModel):
    user_id: Optional[int] = None
    model_name: str
    prompt_text: str = Field(max_length=150)
    category: str
    rate: int = Field(ge=1, le=5)


class PromptRead(BaseModel):
    id: int
    model_name: str
    prompt_text: str
    category: str
    rate: int

    class Config:
        from_attributes = True
