from fastapi import APIRouter, Depends

from auth.auth_service import get_current_db_user
from core.prompt_options import CATEGORY_OPTIONS, MODEL_OPTIONS
from models.user import User


router = APIRouter()


@router.get("/categories")
def read_categories(_current_user: User = Depends(get_current_db_user)):
    return {"items": CATEGORY_OPTIONS}


@router.get("/models")
def read_models(_current_user: User = Depends(get_current_db_user)):
    return {"items": MODEL_OPTIONS}
