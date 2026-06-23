from fastapi import APIRouter, HTTPException, Depends, Body, Query
from sqlmodel import Session, select
from models.user import User
from passlib.hash import sha256_crypt
from db.db_connection import get_session
from auth.auth_service import authenticate_user, crear_jwt, get_current_user, get_current_db_user
from infrastructure.email.smtp_service import send_email
import secrets
import base64
import re
import binascii

from redis import Redis
from db.redis_connection import get_redis
from pydantic import BaseModel, Field
from schemas.login_schema import LoginRequest
from schemas.user_schema import UserCreate, UserRead

router = APIRouter()


class RecoveryGenerateRequest(BaseModel):
    username: str
    ttl: int = Field(default=300, ge=60, le=3600)


class RecoveryRedeemRequest(BaseModel):
    key: str


@router.post("/signup")
def signup(payload: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == payload.username)
    result = session.exec(statement)
    user_exists = result.one_or_none()
    if user_exists:
        raise HTTPException(status_code=400, detail="username already taken")
    if payload.role not in {"user", "admin", "god"}:
        raise HTTPException(status_code=400, detail="invalid role")
    user = User(
        username=payload.username,
        name=payload.name,
        last_name=payload.last_name,
        email=payload.email,
        hashed_password=sha256_crypt.hash(payload.password),
        role=payload.role,
    )
    session.add(user)
    session.commit()
    return {"message": "User created successfully"}

@router.post("/login")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate_user(request.username, request.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = crear_jwt(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=UserRead)
def profile(current_user: User = Depends(get_current_db_user)):
    return current_user


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_db_user)):
    return current_user


@router.get("/token-profile")
def token_profile(current_user: dict = Depends(get_current_user)):
    return {"profile data": current_user}


def _resolve_generate_request(body: RecoveryGenerateRequest | None, username: str | None, ttl: int) -> RecoveryGenerateRequest:
    if body:
        return body
    if not username:
        raise HTTPException(status_code=422, detail="username is required")
    return RecoveryGenerateRequest(username=username, ttl=ttl)


def _resolve_recover_request(body: RecoveryRedeemRequest | None, key: str | None) -> RecoveryRedeemRequest:
    if body:
        return body
    if not key:
        raise HTTPException(status_code=422, detail="key is required")
    return RecoveryRedeemRequest(key=key)

@router.post("/generate")
async def generate_password(
    body: RecoveryGenerateRequest | None = Body(default=None),
    username: str | None = Query(default=None),
    ttl: int = Query(default=300, ge=60, le=3600),
    redis: Redis = Depends(get_redis),
    session: Session = Depends(get_session)
):
    request = _resolve_generate_request(body, username, ttl)
    statement = select(User).where(User.username == request.username)
    result = session.exec(statement)
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    """Generate random key"""
    encoded = base64.b64encode(request.username.encode('utf-8')).decode('utf-8')
    key = f"{secrets.token_hex(16)}.{encoded}"
    if redis.exists(key):
        raise HTTPException(status_code=400, detail="Key already exists")
    """Generate and store a temporary password"""
    password = secrets.token_urlsafe(16)
    user.hashed_password = sha256_crypt.hash(password)
    session.add(user)
    session.commit()
    session.refresh(user)
    email_body = f"Hey {user.username} this is your recovery key:\n--> {key} <--\nit expires in {request.ttl/60}"
    await send_email(user.email, user.username, email_body)
    redis.setex(key, request.ttl, password)

    return {"message": f"Message sent successfully, it expires in {request.ttl/60} minutes"}

@router.post("/recover")
def recover_password(
    body: RecoveryRedeemRequest | None = Body(default=None),
    key: str | None = Query(default=None),
    redis: Redis = Depends(get_redis),
    session: Session = Depends(get_session)
):
    request = _resolve_recover_request(body, key)
    key = request.key

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
