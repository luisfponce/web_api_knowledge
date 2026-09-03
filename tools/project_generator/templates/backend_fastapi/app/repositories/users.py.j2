from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email_or_username(session: Session, *, email: str, username: str) -> User | None:
    statement = select(User).where(or_(User.email == email, User.username == username))
    return session.scalar(statement)


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.scalar(select(User).where(User.username == username))


def create_user(session: Session, *, email: str, username: str, password_hash: str) -> User:
    user = User(email=email, username=username, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
