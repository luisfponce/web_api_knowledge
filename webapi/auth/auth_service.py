import re
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.hash import sha256_crypt
from sqlmodel import Session, select

from core import config
from db.db_connection import get_session
from dotenv import load_dotenv
from models.user import User

load_dotenv()

SECRET_KEY = config.JWT_SECRET_KEY
ALGORITHM = config.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES


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


def crear_jwt(data: dict):
    payload = {
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "data": data
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# Validar un token con prefijo "Bearer" (compatibilidad legado)
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
    except Exception:  # pylint: disable=broad-exception-caught
        return None


# Validar token puro (sin prefijo "Bearer")
def validar_jwt_raw(token: str):
    try:
        if not token:
            return None
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["data"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:  # pylint: disable=broad-exception-caught
        return None


# Esquema HTTPBearer — registra el Security Scheme en OpenAPI (/docs)
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """Dependencia reutilizable para endpoints protegidos con Bearer token."""
    data = validar_jwt_raw(credentials.credentials)
    if not data:
        raise HTTPException(status_code=401, detail="Unauthorized token")
    return data