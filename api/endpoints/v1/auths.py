from fastapi import APIRouter, HTTPException, Depends, Header
from sqlmodel import Session, select
from models.user import User
from typing import Optional
from passlib.hash import sha256_crypt
from db.db_connection import get_session
from auth.auth_service import authenticate_user, crear_jwt, validar_jwt

router = APIRouter()


@router.post("/signup")
def signup(user: User, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    result = session.exec(statement)
    user_exists = result.one_or_none()
    if user_exists:
        raise HTTPException(status_code=400, detail="username already taken")
    user.hashed_password = sha256_crypt.hash(user.hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created successfully"}

@router.post("/login")
def login(username: str, password: str, session: Session = Depends(get_session)):

    user = authenticate_user(username, password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = crear_jwt(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile")
def profile(authorization: Optional[str] = Header(None)):
    data = validar_jwt(authorization)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    return {"profile darta": data}