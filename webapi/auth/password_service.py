from passlib.context import CryptContext
from passlib.exc import UnknownHashError


password_context = CryptContext(
    schemes=["argon2", "sha256_crypt"],
    deprecated=["sha256_crypt"],
    argon2__type="ID",
)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_context.verify(password, password_hash)
    except (TypeError, ValueError, UnknownHashError):
        return False


def password_hash_needs_update(password_hash: str) -> bool:
    try:
        return password_context.needs_update(password_hash)
    except (TypeError, ValueError, UnknownHashError):
        return False
