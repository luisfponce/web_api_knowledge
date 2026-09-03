from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.models.item import Item
from app.repositories import items as item_repository
from app.schemas.item import ItemCreate, ItemUpdate


def list_items(session: Session) -> list[Item]:
    return item_repository.list_items(session)


def get_item(session: Session, item_id: int) -> Item:
    item = item_repository.get_item(session, item_id)
    if item is None:
        raise not_found("Item")
    return item


def create_item(session: Session, payload: ItemCreate) -> Item:
    return item_repository.create_item(session, payload)


def update_item(session: Session, item_id: int, payload: ItemUpdate) -> Item:
    return item_repository.update_item(session, get_item(session, item_id), payload)


def delete_item(session: Session, item_id: int) -> None:
    item_repository.delete_item(session, get_item(session, item_id))
