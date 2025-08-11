from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import CHAR
import models


class Cards(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    card_type: str = Field(max_length=10, nullable=False)
    card_number: str = Field(sa_type=CHAR(16), nullable=False, unique=True)
    expiration_date: str = Field(max_length=7, nullable=False)  # MM/YYYY format

    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
        back_populates="cards"
    )