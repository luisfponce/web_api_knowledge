from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services import items as item_service

router = APIRouter()


@router.get("", response_model=list[ItemRead])
def list_items(session: Session = Depends(get_session)) -> list[ItemRead]:
    return item_service.list_items(session)


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, session: Session = Depends(get_session)) -> ItemRead:
    return item_service.create_item(session, payload)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: Session = Depends(get_session)) -> ItemRead:
    return item_service.get_item(session, item_id)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, session: Session = Depends(get_session)) -> ItemRead:
    return item_service.update_item(session, item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: Session = Depends(get_session)) -> Response:
    item_service.delete_item(session, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
