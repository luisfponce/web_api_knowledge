from fastapi import APIRouter
from .endpoints.v1 import auths, users, prompts

api_router = APIRouter()
api_router.include_router(auths.router, prefix="/auth", tags=["Auth"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["Prompts"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
