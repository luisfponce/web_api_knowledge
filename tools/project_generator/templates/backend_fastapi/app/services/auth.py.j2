from sqlalchemy.orm import Session

from app.core.errors import conflict
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import users as user_repository
from app.schemas.auth import RegistrationRead, TokenRead
from app.schemas.user import UserCreate


def register_user(session: Session, payload: UserCreate) -> RegistrationRead:
    existing = user_repository.get_user_by_email_or_username(
        session,
        email=payload.email,
        username=payload.username,
    )
    if existing is not None:
        raise conflict("Registration information is already in use.", code="user_exists")
    user = user_repository.create_user(
        session,
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    token = TokenRead(access_token=create_access_token(str(user.id), {"username": user.username}))
    return RegistrationRead(user=user, token=token)


def authenticate_user(session: Session, *, username: str, password: str) -> TokenRead | None:
    user = user_repository.get_user_by_username(session, username)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return TokenRead(access_token=create_access_token(str(user.id), {"username": user.username}))


def get_current_user(session: Session, subject: str) -> User | None:
    try:
        user_id = int(subject)
    except ValueError:
        return None
    return session.get(User, user_id)
