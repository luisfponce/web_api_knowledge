from fastapi import FastAPI, HTTPException, Depends, Response, Cookie, Header
from typing import Optional
from sqlmodel import Session, select
from passlib.hash import sha256_crypt
import secrets
from datetime import datetime, timedelta
import uvicorn

from database.models import User, Cards, UserReadWithCards, UserSession
from database.db_connection import get_session
from auth.login import authenticate_user, get_current_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, crear_jwt, validar_jwt
# from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

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

@app.get("/")
def root():
    return {"Bank App": "This is a simple app using FastAPI and mariadb."}
###############################################################################


# CRUD -> Create
@app.post("/signup")
def signup(user: User, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    result = session.exec(statement)
    user_exists = result.one_or_none()
    if user_exists:
        raise HTTPException(status_code=400, detail="username already taken")
    user.hashed_password = sha256_crypt.hash(user.hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created successfully"}

@app.post("/login")
def login(username: str, password: str, session: Session = Depends(get_session)):

    user = authenticate_user(username, password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = crear_jwt(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/cards/", response_model=Cards)
def create_card(card: Cards, session: Session = Depends(get_session),
                current_user: dict = Depends(get_current_user)):
    
    # Ensure the user exists before creating a card
    user = session.get(User, card.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.add(card)
    session.commit()
    session.refresh(card)
    return card

###############################################################################
# CRUD -> Read
@app.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    return {"username": current_user.username, "id": current_user.id}


# curl -X POST "http://localhost:8000/login?username=lfponcen&password=lfponcen" -v  <-- to get the session_token thru the cookie
# curl -b session_token=(gotten from verbose) -X GET "http://localhost:8000/users"
@app.get("/users", response_model=list[User])
def read_users(phone: Optional[int] = None, skip: int = 0, limit: int = 10,
               session: Session = Depends(get_session),
               authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ")
    data = validar_jwt(token[1])  # Validate JWT token
    if not data:
        raise HTTPException(status_code=401, detail="Invalid token")
    statement = select(User).offset(skip).limit(limit)
    # If phone is provided, filter by phone number
    if phone:
        statement = statement.where(User.phone == phone)
    users = session.exec(statement).all()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session),
             current_user: dict = Depends(get_current_user)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/cards/", response_model=list[Cards])
def read_cards(skip: int = 0, limit: int = 10,
               session: Session = Depends(get_session),
               current_user: dict = Depends(get_current_user)):
    
    statement = select(Cards).offset(skip).limit(limit)
    cards = session.exec(statement).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No cards found")
    return cards

@app.get("/cards/{card_id}", response_model=Cards)
def get_card(card_id: int, session: Session = Depends(get_session),
             current_user: dict = Depends(get_current_user)):
    
    card = session.get(Cards, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.get("/user/cards/{user_id}", response_model=UserReadWithCards)
def get_user_with_cards(user_id: int, session: Session = Depends(get_session),
                        current_user: dict = Depends(get_current_user)):
    
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Access cards within session to trigger lazy load
    _ = user.cards
    return user
###############################################################################
# CRUD -> Update
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User,
                session: Session = Depends(get_session),
                current_user: dict = Depends(get_current_user)):
    
    user.name = user.name.lower()
    user.last_name = user.last_name.lower()
    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_user.name = user.name
    existing_user.last_name = user.last_name
    existing_user.phone = user.phone
    existing_user.email = user.email
    existing_user.hashed_password = sha256_crypt.hash(user.hashed_password)  # Hash the password
    # Ensure the username is unique
    statement = select(User).where(User.username == user.username, User.id != user_id)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="username already taken")
    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return existing_user

@app.put("/cards/{card_id}", response_model=Cards)
def update_card(card_id: int, card: Cards,
                session: Session = Depends(get_session),
                current_user: dict = Depends(get_current_user)):
    
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
###############################################################################
# CRUD -> Delete
@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session),
                current_user: dict = Depends(get_current_user)):
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
def delete_card(card_id: int, session: Session = Depends(get_session),
                current_user: dict = Depends(get_current_user)):
    
    card = session.get(Cards, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found to delete")
    session.delete(card)
    session.commit()
    return card
##########################################################################################

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
