from fastapi import APIRouter, HTTPException, Depends, Header
from sqlmodel import Session, select
from models.user import User
from typing import Optional
from schemas.user_schema import UserReadWithCards
from db.db_connection import get_session
from auth.auth_service import validar_jwt
from passlib.hash import sha256_crypt


router = APIRouter()

# curl -X POST "http://localhost:8000/login?username=lfponcen&password=lfponcen" -v  <-- to get the session_token thru the cookie
# curl -b session_token=(gotten from verbose) -X GET "http://localhost:8000"
@router.get("", response_model=list[User])
def read_users(phone: Optional[int] = None, skip: int = 0, limit: int = 10,
               session: Session = Depends(get_session),
                   authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    statement = select(User).offset(skip).limit(limit)
    # If phone is provided, filter by phone number
    if phone:
        statement = statement.where(User.phone == phone)
    users = session.exec(statement).all()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session),
               authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/cards/{user_id}", response_model=UserReadWithCards)
def get_user_with_cards(user_id: int, session: Session = Depends(get_session),
               authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Access cards within session to trigger lazy load
    _ = user.cards
    return user

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: User,
                session: Session = Depends(get_session),
                   authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    user.name = user.name.lower()
    user.last_name = user.last_name.lower()
    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_user.name = user.name
    existing_user.last_name = user.last_name
    existing_user.phone = user.phone
    existing_user.email = user.email
    existing_user.hashed_password = sha256_crypt.hash(user.hashed_password)
    # Ensure the username is unique
    statement = select(User).where(User.username == user.username, User.id != user_id)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="username already taken")
    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return existing_user


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session),
                authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found to delete")
        session.delete(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
    return user