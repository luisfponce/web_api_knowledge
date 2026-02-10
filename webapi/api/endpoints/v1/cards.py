from fastapi import APIRouter, HTTPException, Depends, Header
from sqlmodel import Session, select
from typing import Optional
from models.user import User
from models.card import Cards
from db.db_connection import get_session
from auth.auth_service import validar_jwt
from infrastructure.email.smtp_service import send_email

router = APIRouter()

@router.post("/cards", response_model=Cards)
async def create_card(
    card: Cards,
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None),
    send_email_header: Optional[str] = Header(None, alias="send_email")
):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    # Ensure the user exists before creating a card
    user = session.get(User, card.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if str(send_email_header).lower() != "false":
        await send_email(user.email, user.username)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card

@router.get("", response_model=list[Cards])
def read_cards(skip: int = 0, limit: int = 10,
               session: Session = Depends(get_session),
                   authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    statement = select(Cards).offset(skip).limit(limit)
    cards = session.exec(statement).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No cards found")
    return cards


@router.get("/cards/{card_id}", response_model=Cards)
def get_card(card_id: int, session: Session = Depends(get_session),
                   authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    card = session.get(Cards, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.put("/cards/{card_id}", response_model=Cards)
def update_card(card_id: int, card: Cards,
                session: Session = Depends(get_session),
                   authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token") 
    existing_card = session.get(Cards, card_id)
    if not existing_card:
        raise HTTPException(status_code=404, detail="Card not found")
    existing_card.card_type = card.card_type
    existing_card.card_number = card.card_number
    existing_card.expiration_date = card.expiration_date
    existing_card.user_id = card.user_id  # Ensure the user exists
    user = session.get(User, card.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found for this card")
    session.add(existing_card)
    session.commit()
    session.refresh(existing_card)
    return existing_card


@router.delete("/cards/{card_id}")
def delete_card(card_id: int, session: Session = Depends(get_session),
                   authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    card = session.get(Cards, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found to delete")
    session.delete(card)
    session.commit()
    return card
