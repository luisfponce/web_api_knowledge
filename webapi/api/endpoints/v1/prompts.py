from fastapi import APIRouter, HTTPException, Depends, Header
from sqlmodel import Session, select
from typing import Optional
from models.user import User
from models.prompts import Prompts
from db.db_connection import get_session
from auth.auth_service import get_current_db_user
from infrastructure.email.smtp_service import send_email
from schemas.prompt_schema import PromptCreate

router = APIRouter()

@router.post("", response_model=Prompts)
async def create_prompt(
    prompt: PromptCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_db_user),
    send_email_header: Optional[str] = Header("false", alias="send_email")
):
    target_user_id = prompt.user_id or current_user.id
    prompt_user = session.get(User, target_user_id)
    if not prompt_user:
        raise HTTPException(status_code=404, detail="User not found")
    if prompt_user.id != current_user.id and current_user.role != "god":
        raise HTTPException(status_code=403, detail="Cannot create prompts for another user")

    created_prompt = Prompts(
        user_id=prompt_user.id,
        model_name=prompt.model_name,
        prompt_text=prompt.prompt_text,
        category=prompt.category,
        rate=prompt.rate,
    )

    session.add(created_prompt)
    session.commit()
    session.refresh(created_prompt)

    # Email notification is best-effort and should not block prompt persistence.
    if str(send_email_header).lower() == "true":
        try:
            await send_email(prompt_user.email, prompt_user.username)
        except Exception:
            pass

    return created_prompt

@router.get("", response_model=list[Prompts])
def read_prompts(
    skip: int = 0,
    limit: int = 10,
    user_id: Optional[int] = None,
    category: Optional[str] = None,
    model_name: Optional[str] = None,
    rate: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_db_user),
):
    statement = select(Prompts)
    if current_user.role not in {"admin", "god"}:
        statement = statement.where(Prompts.user_id == current_user.id)
    elif user_id is not None:
        statement = statement.where(Prompts.user_id == user_id)
    if category:
        statement = statement.where(Prompts.category == category)
    if model_name:
        statement = statement.where(Prompts.model_name == model_name)
    if rate is not None:
        statement = statement.where(Prompts.rate == rate)
    statement = statement.offset(skip).limit(limit)
    prompts = session.exec(statement).all()
    if not prompts:
        raise HTTPException(status_code=404, detail="No prompts found")
    return prompts


@router.get("/{prompt_id}", response_model=Prompts)
def get_prompt(prompt_id: int, session: Session = Depends(get_session),
               current_user: User = Depends(get_current_db_user)):
    prompt = session.get(Prompts, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    if prompt.user_id != current_user.id and current_user.role not in {"admin", "god"}:
        raise HTTPException(status_code=403, detail="Cannot access this prompt")
    return prompt

@router.put("/{prompt_id}", response_model=Prompts)
def update_prompt(prompt_id: int, prompt: PromptCreate,
                session: Session = Depends(get_session),
                current_user: User = Depends(get_current_db_user)):
    existing_prompt = session.get(Prompts, prompt_id)
    if not existing_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins cannot update prompts")
    if existing_prompt.user_id != current_user.id and current_user.role != "god":
        raise HTTPException(status_code=403, detail="Cannot update another user's prompt")

    target_user_id = prompt.user_id or existing_prompt.user_id
    user = session.get(User, target_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found for this prompt")
    if target_user_id != existing_prompt.user_id and current_user.role != "god":
        raise HTTPException(status_code=403, detail="Cannot reassign this prompt")
    existing_prompt.model_name = prompt.model_name
    existing_prompt.prompt_text = prompt.prompt_text
    existing_prompt.category = prompt.category
    existing_prompt.rate = prompt.rate
    existing_prompt.user_id = target_user_id
    session.add(existing_prompt)
    session.commit()
    session.refresh(existing_prompt)
    return existing_prompt


@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: int, session: Session = Depends(get_session),
                current_user: User = Depends(get_current_db_user)):
    prompt = session.get(Prompts, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found to delete")
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins cannot delete prompts")
    if prompt.user_id != current_user.id and current_user.role != "god":
        raise HTTPException(status_code=403, detail="Cannot delete another user's prompt")
    session.delete(prompt)
    session.commit()
    return prompt
