from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import json
import os
import uvicorn

JSON_FILENAME = "phonebook.json"

# Use json as database:
# https://dev.to/ahmed__elboshi/learn-how-to-use-json-as-a-small-database-for-your-python-projects-by-building-a-hotel-accounting-system-47b4

app = FastAPI()
@app.get("/")
def root():
    return {"Phonebook App": "Hello! This is a simple phonebook app using FastAPI and a JSON file as a database."}

# CRUD -> Create
@app.post("/users")
def create_user(name: str, last_name: str, phone: int, email: str, address: str):
    # example:
    # http://127.0.0.1:8000/users?name=%22Luis%22&last_name=%22Ponce%22&phone=33112233&email=%22test%40example.com%22&address=%22myaddress%22
    try:
        with open(JSON_FILENAME, 'r') as file:
            data = json.load(file)
    except:
        data = {}
    user = {
        "name": name,
        "last_name": last_name,
        "phone": phone,
        "email": email,
        "address": address
    }
    fn = f"{name.lower()} {last_name.lower()}"
    data[fn] = user
    with open(JSON_FILENAME, 'w') as file:
        json.dump(data, file, indent=4)
    return user

# CRUD -> Read
@app.get("/users")
def read_users():
    if os.path.isfile(JSON_FILENAME) and os.access(JSON_FILENAME, os.R_OK):
        with open(JSON_FILENAME, "r") as file:
            try:
                data = json.load(file)
            except:
                data = {}
    else:
        raise HTTPException(status_code=404, detail="read_users: Phonebook file not found or not readable")
    return data

@app.get("/users/{user_name}")
# siempre tiene prioridad el PATH, y luego la query string
def get_user(user_name: str, phone: Optional[int] = None) -> dict:
    user_name = user_name.lower()
    with open(JSON_FILENAME, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(status_code=404, detail="get_user: Could not read read_users phonebook")
    if phone != None:
        for u in data.values():
            if u["phone"] == phone:
                return u
    else:
        for k in data.keys():
            if k == user_name:
                return data[k]
    raise HTTPException(status_code=404, detail="User not found")

# CRUD -> Update
@app.put("/users/{user_name}")
def update_user(user_name: str, phone: int, email: str, address: str):
    user_name = user_name.lower()
    with open(JSON_FILENAME, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(status_code=404, detail="update_user: Could not read phonebook")
    for k in data.keys():
        if k == user_name:
            user = data[k]
            user["phone"] = phone
            user["email"] = email
            user["address"] = address
            data[k] = user
            with open(JSON_FILENAME, "w") as file:
                json.dump(data, file)
            return user
    raise HTTPException(status_code=404, detail="User not found")

# CRUD -> Delete
@app.delete("/users/{user_name}")
def delete_user(user_name: str):
    user_name = user_name.lower()
    with open(JSON_FILENAME, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(status_code=404, detail="delete_user: Could not read phonebook")
    
    for k in data.keys():
        if k == user_name:
            user = data[k]
            del data[k]
            with open(JSON_FILENAME, "w") as file:
                json.dump(data, file)
            return user
    raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)