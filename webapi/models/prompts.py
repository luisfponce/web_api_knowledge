from typing import Optional

from sqlmodel import Field, Relationship, SQLModel



class Prompts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    model_name: str = Field(max_length=30, nullable=False)
    prompt_text: str = Field(max_length=150, nullable=False)
    category: str = Field(max_length=30, nullable=False)
    rate: int = Field(nullable=False, ge=1, le=5)

    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
        back_populates="prompts"
    )
