from typing import Optional

from sqlalchemy import Column, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlmodel import Field, Relationship, SQLModel


PROMPT_TEXT_MAX_CHARS = 1_000_000
PROMPT_TEXT_SQL_TYPE = (
    Text()
    .with_variant(LONGTEXT(), "mysql")
    .with_variant(LONGTEXT(), "mariadb")
)


class Prompts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    model_name: str = Field(max_length=30, nullable=False)
    prompt_text: str = Field(sa_column=Column(PROMPT_TEXT_SQL_TYPE, nullable=False))
    category: str = Field(max_length=30, nullable=False)
    rate: int = Field(nullable=False, ge=1, le=5)

    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
        back_populates="prompts",
    )
