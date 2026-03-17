from typing import Optional

from pydantic import BaseModel


class PromptCreate(BaseModel):
    user_id: Optional[int] = None
    model_name: str
    prompt_text: str
    category: str
    rate: str


class PromptRead(BaseModel):
    id: int
    model_name: str
    prompt_text: str
    category: str
    rate: str

    class Config:
        from_attributes = True
