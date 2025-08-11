from fastapi import HTTPException, Depends
from typing import Optional
from sqlmodel import Session, select
from models.user import User
from db.db_connection import get_session
from datetime import datetime, timedelta
import jwt
from passlib.hash import sha256_crypt
import re
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("ENV_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def authenticate_user(username: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not sha256_crypt.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Crear un token
def crear_jwt(data: dict):
    payload = {
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "data": data
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Validar un token
def validar_jwt(token: str):
    try:
        if not token:
            raise HTTPException(status_code=401, detail="No token given to authenticate")
        match = re.match(r"^[B,b]earer\s+(.+)$", token)
        if not match:
            raise HTTPException(status_code=401, detail="Invalid token format")
        token = match.group(1)
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized token")
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["data"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None
    