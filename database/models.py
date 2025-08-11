from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import CHAR, TEXT
from pydantic import BaseModel
from datetime import datetime


class Cards(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    card_type: str = Field(max_length=10, nullable=False)
    card_number: str = Field(sa_type=CHAR(16), nullable=False, unique=True)
    expiration_date: str = Field(max_length=7, nullable=False)  # MM/YYYY format

    user: Optional["User"] = Relationship(back_populates="cards")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, index=True, nullable=False)
    name: str = Field(max_length=100, index=True, nullable=False)
    last_name: str = Field(max_length=100, index=True, nullable=False)
    phone: Optional[int] = Field(default=12, index=True, unique=True) # Check why numbers lengh like 10 digits is not working
    email: str = Field(max_length=100, nullable=False)
    hashed_password: str = Field(max_length=100, unique=True)

    cards: List[Cards] = Relationship(back_populates="user")


class UserSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str = Field(sa_type=TEXT, nullable=False, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

# NON ORM MODELS


class CardRead(BaseModel):
    id: int
    card_type: str
    card_number: str
    expiration_date: str

    class Config:
        orm_mode = True


class UserReadWithCards(BaseModel):
    id: int
    name: str
    last_name: str
    phone: Optional[int]
    email: str
    cards: List[CardRead] = []

    class Config:
        orm_mode = True
