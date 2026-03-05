from typing import Optional, List

from pydantic import EmailStr
from sqlalchemy import BIGINT
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, index=True, nullable=False)
    name: str = Field(max_length=100, index=True, nullable=False)
    last_name: str = Field(max_length=100, index=True, nullable=False)
    phone: Optional[int] = Field(default=None, sa_type=BIGINT, index=True, unique=True)
    email: EmailStr = Field(max_length=100, nullable=False)
    hashed_password: str = Field(max_length=255)  # Longer for bcrypt hashes

    prompts: List["Prompts"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
        back_populates="user"
    )
