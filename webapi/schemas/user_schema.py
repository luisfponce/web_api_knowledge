from typing import Optional, List
from pydantic import BaseModel
from .card_schema import CardRead

class UserReadWithCards(BaseModel):
    id: int
    name: str
    last_name: str
    phone: Optional[int]
    email: str
    cards: List[CardRead] = []

    class Config:
        from_attributes = True