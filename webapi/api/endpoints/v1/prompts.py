from fastapi import APIRouter, HTTPException, Depends, Header
from sqlmodel import Session, select
from typing import Optional
from models.user import User
from models.prompts import Prompts
from db.db_connection import get_session
from auth.auth_service import get_current_user
from infrastructure.email.smtp_service import send_email

router = APIRouter()


@router.post("", response_model=Prompts)
async def create_prompt(
    prompt: Prompts,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    send_email_header: Optional[str] = Header("false", alias="send_email"),
):
    # Ensure the user exists before creating a prompt
    user = session.get(User, prompt.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.add(prompt)
    session.commit()
    session.refresh(prompt)

    # Email notification is best-effort and should not block prompt persistence.
    if str(send_email_header).lower() == "true":
        try:
            await send_email(user.email, user.username)
        except Exception:
            pass

    return prompt


@router.get("", response_model=list[Prompts])
def read_prompts(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    statement = select(Prompts).offset(skip).limit(limit)
    prompts = session.exec(statement).all()
    if not prompts:
        raise HTTPException(status_code=404, detail="No prompts found")
    return prompts


@router.get("/{prompt_id}", response_model=Prompts)
def get_prompt(
    prompt_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    prompt = session.get(Prompts, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.put("/{prompt_id}", response_model=Prompts)
def update_prompt(
    prompt_id: int,
    prompt: Prompts,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    existing_prompt = session.get(Prompts, prompt_id)
    if not existing_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    existing_prompt.model_name = prompt.model_name
    existing_prompt.prompt_text = prompt.prompt_text
    existing_prompt.category = prompt.category
    existing_prompt.rate = prompt.rate
    existing_prompt.user_id = prompt.user_id  # Ensure the user exists
    user = session.get(User, prompt.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found for this prompt")
    session.add(existing_prompt)
    session.commit()
    session.refresh(existing_prompt)
    return existing_prompt


@router.delete("/{prompt_id}")
def delete_prompt(
    prompt_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    prompt = session.get(Prompts, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found to delete")
    session.delete(prompt)
    session.commit()
    return prompt
