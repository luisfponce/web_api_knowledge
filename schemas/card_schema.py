from pydantic import BaseModel


class CardRead(BaseModel):
    id: int
    card_type: str
    card_number: str
    expiration_date: str

    class Config:
        from_attributes = True

