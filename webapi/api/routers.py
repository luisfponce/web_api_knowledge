from fastapi import APIRouter
from .endpoints.v1 import auths, users, cards

api_router = APIRouter()
api_router.include_router(auths.router, prefix="/auth", tags=["Auth"])
api_router.include_router(cards.router, prefix="/cards", tags=["Cards"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])