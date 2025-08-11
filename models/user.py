from typing import Optional, List
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import BIGINT
import models


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, index=True, nullable=False)
    name: str = Field(max_length=100, index=True, nullable=False)
    last_name: str = Field(max_length=100, index=True, nullable=False)
    #phone: Optional[int] = Field(default=12, sa_type=BIGINT, index=True, unique=True) # Check why numbers lengh like 10 digits is not working
    phone: Optional[int] = Field(default=None, sa_type=BIGINT, index=True, unique=True)
    email: EmailStr = Field(max_length=100, nullable=False)
    hashed_password: str = Field(max_length=255)  # Longer for bcrypt hashes

    cards: List["Cards"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}, 
        back_populates="user"
    )