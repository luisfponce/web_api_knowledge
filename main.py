from fastapi import FastAPI, HTTPException, Query, Depends
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select
import uvicorn

JSON_FILENAME = "phonebook.json"

app = FastAPI()
@app.get("/")
def root():
    return {"Phonebook App": "Hello! This is a simple phonebook app using FastAPI and a JSON file as a database."}

###################################### M O D E L S ######################################
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    last_name: str = Field(index=True, nullable=False)
    phone: int | None = Field(default=None, index=True, unique=True)
    email: str = Field(max_length=100, nullable=False)
    address: str = Field(max_length=200, default="")

##########################################################################################
# sqlite works as a file sstem, it is not aimed for database server
DATABASE_URL = "sqlite:///./phonebook.db"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
##########################################################################################

# CRUD -> Create
@app.post("/users/", response_model=User)
"""
    user post example:
    {
    "name": "Luis",
    "last_name": "Ponce",
    "phone": 33112213,
    "email": "luis@example.com",
    "address": "myaddress"
    }
"""
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


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

# CRUD -> Delete
@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found to delete")
    session.delete(user)
    session.commit()
    return user

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
