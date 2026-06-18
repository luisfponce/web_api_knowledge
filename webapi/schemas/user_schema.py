from typing import List
from pydantic import BaseModel
from .prompt_schema import PromptRead


class UserRead(BaseModel):
    id: int
    username: str
    name: str
    last_name: str
    email: str
    role: str

    class Config:
        from_attributes = True

class UserReadWithPrompts(BaseModel):
    id: int
    username: str
    name: str
    last_name: str
    email: str
    role: str
    prompts: List[PromptRead] = []

    class Config:
        from_attributes = True
