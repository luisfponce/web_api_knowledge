from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import decode_access_token
from app.db.session import get_session
from app.schemas.auth import RegistrationRead, TokenRead
from app.schemas.user import UserCreate, UserRead
from app.services import auth as auth_service

router = APIRouter()


@router.post("/register", response_model=RegistrationRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, session: Session = Depends(get_session)) -> RegistrationRead:
    return auth_service.register_user(session, payload)


@router.post("/token", response_model=TokenRead)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> TokenRead:
    token = auth_service.authenticate_user(session, username=form.username, password=form.password)
    if token is None:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_credentials",
            detail="Username or password is incorrect.",
        )
    return token


@router.get("/me", response_model=UserRead)
def profile(
    claims: dict = Depends(decode_access_token),
    session: Session = Depends(get_session),
) -> UserRead:
    user = auth_service.get_current_user(session, str(claims.get("sub", "")))
    if user is None:
        raise ApiError(status_code=status.HTTP_401_UNAUTHORIZED, code="invalid_token", detail="User not found.")
    return user
