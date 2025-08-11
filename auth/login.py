from fastapi import HTTPException, Depends
from typing import Optional
from sqlmodel import Session, select
from database.models import User
from database.db_connection import get_session
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import sha256_crypt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "testkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def authenticate_user(username: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not sha256_crypt.verify(password, user.hashed_password):
        raise None
    return user

def get_current_user(token: str = Depends(oauth2_scheme),
                        session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
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
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["data"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None
    