from fastapi import APIRouter, HTTPException, Depends, Header
from sqlmodel import Session, select
from models.user import User
from typing import Optional
from passlib.hash import sha256_crypt
from db.db_connection import get_session
from auth.auth_service import authenticate_user, crear_jwt, validar_jwt
from infrastructure.email.smtp_service import send_email
import secrets
import base64
import re
import binascii

from redis import Redis
from db.redis_connection import get_redis
from schemas.login_schema import LoginRequest

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
def login(request: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate_user(request.username, request.password, session)
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

@router.post("/generate")
async def generate_password(
    username: str,
    ttl: int = 300,
    redis: Redis = Depends(get_redis),
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == username)
    result = session.exec(statement)
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    """Generate random key"""
    encoded = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    key = f"{secrets.token_hex(16)}.{encoded}"
    if redis.exists(key):
        raise HTTPException(status_code=400, detail="Key already exists")
    """Generate and store a temporary password"""
    password = secrets.token_urlsafe(16)
    user.hashed_password = sha256_crypt.hash(password)
    session.add(user)
    session.commit()
    session.refresh(user)
    email_body = f"Hey {user.username} this is your recovery key:\n--> {key} <--\nit expires in {ttl/60}"
    await send_email(user.email, user.username, email_body)
    redis.setex(key, ttl, password)

    return {f"Message sent successfully, it expires in {ttl/60} minutes"}

@router.post("/recover")
def recover_password(
    key: str,
    redis: Redis = Depends(get_redis),
    session: Session = Depends(get_session)
):

    match = re.search(r"\.(.+)$", key)
    if not match:
        raise HTTPException(status_code=401, detail="Invalid key format")
    username = match.group(1)
    if not username:
        raise HTTPException(status_code=401, detail="Unauthorized key")
    username = username.strip().replace(" ", "").replace("\n", "")
    missing_padding = len(username) % 4
    if missing_padding:
        username += "=" * (4 - missing_padding)
    try:
        username = base64.b64decode(username).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError) as e:
        raise HTTPException(status_code=401, detail=f"Decode error: {e}")
    statement = select(User).where(User.username == username)
    result = session.exec(statement)
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Key corrputed")
    """Retrieve a temporary password if it exists"""
    password = redis.get(key)
    if password is None:
        raise HTTPException(status_code=404, detail="Password not found in redis or expired")
    return {"key": key, "password": password}
