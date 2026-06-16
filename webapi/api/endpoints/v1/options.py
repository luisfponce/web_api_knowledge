from fastapi import APIRouter, Depends

from auth.auth_service import get_current_db_user
from models.user import User


router = APIRouter()

CATEGORY_OPTIONS = [
    {"value": "qa", "label": "QA"},
    {"value": "dev", "label": "Development"},
    {"value": "ops", "label": "Operations"},
    {"value": "writing", "label": "Writing"},
    {"value": "research", "label": "Research"},
]

MODEL_OPTIONS = [
    {"value": "gpt-4.1", "label": "GPT-4.1"},
    {"value": "gpt-4o-mini", "label": "GPT-4o mini"},
    {"value": "gpt-5", "label": "GPT-5"},
    {"value": "gpt-5-mini", "label": "GPT-5 mini"},
]


@router.get("/categories")
def read_categories(_current_user: User = Depends(get_current_db_user)):
    return {"items": CATEGORY_OPTIONS}


@router.get("/models")
def read_models(_current_user: User = Depends(get_current_db_user)):
    return {"items": MODEL_OPTIONS}
