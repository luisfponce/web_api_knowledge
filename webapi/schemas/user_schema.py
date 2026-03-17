from typing import Optional, List
from pydantic import BaseModel
from .prompt_schema import PromptRead


class UserRead(BaseModel):
    id: int
    username: str
    name: str
    last_name: str
    phone: Optional[int]
    email: str

    class Config:
        from_attributes = True

class UserReadWithPrompts(BaseModel):
    id: int
    username: str
    name: str
    last_name: str
    phone: Optional[int]
    email: str
    prompts: List[PromptRead] = []

    class Config:
        from_attributes = True
