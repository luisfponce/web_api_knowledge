from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from models.user import User
from schemas.user_schema import UserRead, UserReadWithPrompts
from db.db_connection import get_session
from auth.auth_service import get_current_user
from auth.password_service import hash_password
from core.email_utils import normalize_email


router = APIRouter()

@router.get("", response_model=list[UserRead])
def read_users(skip: int = 0, limit: int = 10,
               session: Session = Depends(get_session),
               current_user: dict = Depends(get_current_user)):
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users


@router.get("/prompts/{user_id}", response_model=UserReadWithPrompts)
def get_user_with_prompts(user_id: int, session: Session = Depends(get_session),
               current_user: dict = Depends(get_current_user)):
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Access prompts within session to trigger lazy load
    _ = user.prompts
    return user


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session),
               current_user: dict = Depends(get_current_user)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: User,
                session: Session = Depends(get_session),
                current_user: dict = Depends(get_current_user)):
    user.name = user.name.lower()
    user.last_name = user.last_name.lower()
    email = normalize_email(user.email)
    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Ensure the username is unique
    statement = select(User).where(User.username == user.username, User.id != user_id)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="username already taken")
    statement = select(User).where(User.email == email, User.id != user_id)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="email already taken")
    existing_user.name = user.name
    existing_user.last_name = user.last_name
    existing_user.email = email
    existing_user.hashed_password = hash_password(user.hashed_password)
    session.add(existing_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="user information already in use")
    session.refresh(existing_user)
    return existing_user


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session),
                current_user: dict = Depends(get_current_user)):
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found to delete")
        session.delete(user)
        session.commit()
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
    return user
