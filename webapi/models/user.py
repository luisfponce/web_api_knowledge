from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, index=True, nullable=False)
    name: str = Field(max_length=100, index=True, nullable=False)
    last_name: str = Field(max_length=100, index=True, nullable=False)
    email: EmailStr = Field(max_length=100, nullable=False)
    hashed_password: str = Field(max_length=255)  # Longer for bcrypt hashes
    preferred_language: str = Field(
        default="es",
        max_length=2,
        nullable=False,
        sa_column_kwargs={"server_default": "es"},
    )
    role: str = Field(
        default="user",
        max_length=20,
        nullable=False,
        sa_column_kwargs={"server_default": "user"},
    )

    prompts: List["Prompts"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
        back_populates="user"
    )
