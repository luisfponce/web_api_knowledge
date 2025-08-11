from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship
import os
from sqlalchemy import CHAR
from typing import List, Optional
from pydantic import BaseModel
import uvicorn

"""
Create a MariaDB container for testing purposes.
You can run this command in your terminal to start a MariaDB server with the specified environment variables
and port mapping. Make sure Docker is installed and running on your machine.
docker run --detach \
  --env MARIADB_USER=pbtest \
  --env MARIADB_PASSWORD=pbtest \
  --env MARIADB_DATABASE=bank_db \
  --env MARIADB_RANDOM_ROOT_PASSWORD=1 \
  --name mariadb-server-test \
  -p 3306:3306 \
  mariadb:latest

Ensure that the environment variable DB_URL is set to your MariaDB connection string
Example: export DB_URL="mariadb+mariadbconnector://pbtest:pbtest@127.0.0.1:3306/bank_db"
"""
app = FastAPI()
@app.get("/")
def root():
    return {"Bank App": "Hello! This is a simple bank app using FastAPI and mariadb server."}

###################################### M O D E L S ######################################
class Cards(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    card_type: str = Field(max_length=10, nullable=False)
    card_number: str = Field(sa_type=CHAR(16), nullable=False, unique=True)
    expiration_date: str = Field(max_length=7, nullable=False)  # MM/YYYY format

    user: Optional["User"] = Relationship(back_populates="cards")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True, nullable=False)
    last_name: str = Field(max_length=100, index=True, nullable=False)
    phone: Optional[int] = Field(default=None, index=True, unique=True)
    email: str = Field(max_length=100, nullable=False)
    address: str = Field(max_length=100, default="")

    cards: List[Cards] = Relationship(back_populates="user")

class CardRead(BaseModel):
    id: int
    card_type: str
    card_number: str
    expiration_date: str

    class Config:
        orm_mode = True

class UserReadWithCards(BaseModel):
    id: int
    name: str
    last_name: str
    phone: Optional[int]
    email: str
    address: str
    cards: List[CardRead] = []

    class Config:
        orm_mode = True

##########################################################################################
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    DB_URL = "sqlite:///./bank_db.db"  # Default to SQLite if no environment variable is set

connect_args = {"check_same_thread": False}
engine = create_engine(DB_URL, echo=True)

# Actually create the tables in the database
# If using SQLite, the database file will be created in the current directory
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

##########################################################################################
# CRUD -> Create
@app.post("/users/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post("/cards/", response_model=Cards)
def create_card(card: Cards, session: Session = Depends(get_session)):
    # Ensure the user exists before creating a card
    user = session.get(User, card.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.add(card)
    session.commit()
    session.refresh(card)
    return card
##########################################################################################
# CRUD -> Read
@app.get("/users/", response_model=list[User])
def read_users(phone: Optional[int] = None, skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    statement = select(User).offset(skip).limit(limit)
    # If phone is provided, filter by phone number
    if phone:
        statement = statement.where(User.phone == phone)
    users = session.exec(statement).all()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/cards/", response_model=list[Cards])
def read_cards(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    statement = select(Cards).offset(skip).limit(limit)
    cards = session.exec(statement).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No cards found")
    return cards

@app.get("/cards/{card_id}", response_model=Cards)
def get_card(card_id: int, session: Session = Depends(get_session)):
    card = session.get(Cards, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.get("/user/cards/{user_id}", response_model=UserReadWithCards)
def get_user_with_cards(user_id: int, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Access cards within session to trigger lazy load
    _ = user.cards
    return user
##########################################################################################
# CRUD -> Update
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User, session: Session = Depends(get_session)):
    user.name = user.name.lower()
    user.last_name = user.last_name.lower()
    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_user.name = user.name
    existing_user.last_name = user.last_name
    existing_user.phone = user.phone
    existing_user.email = user.email
    existing_user.address = user.address
    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return existing_user

@app.put("/cards/{card_id}", response_model=Cards)
def update_card(card_id: int, card: Cards, session: Session = Depends(get_session)):
    existing_card = session.get(Cards, card_id)
    if not existing_card:
        raise HTTPException(status_code=404, detail="Card not found")
    existing_card.card_type = card.card_type
    existing_card.card_number = card.card_number
    existing_card.expiration_date = card.expiration_date
    existing_card.user_id = card.user_id  # Ensure the user exists
    user = session.get(User, card.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found for this card")
    session.add(existing_card)
    session.commit()
    session.refresh(existing_card)
    return existing_card
##########################################################################################
# CRUD -> Delete
@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found to delete")
        session.delete(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
    return user

@app.delete("/cards/{card_id}")
def delete_card(card_id: int, session: Session = Depends(get_session)):
    card = session.get(Cards, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found to delete")
    session.delete(card)
    session.commit()
    return card
##########################################################################################

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
