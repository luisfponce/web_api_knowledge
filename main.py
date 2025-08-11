from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

items = []

@app.get("/")
def root():
    return {"Hello": "World"}

# CRUD -> Create
@app.post("/items")
def create_item(item: str):
    items.append(item)
    return {"items": items}

# CRUD -> Read
@app.get("/items")
def read_items():
    return {"items": items}

@app.get("/items/{item_id}")
def get_item(item_id: int) -> str:
    if 0 <= item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")

# CRUD -> Update
@app.put("/items/{item_id}")
def update_item(item_id: int, item: str):
    if 0 <= item_id < len(items):
        items[item_id] = item
        return {"item": items[item_id]}
    else:
        raise HTTPException(status_code=404, detail="Item not found to update")

# CRUD -> Delete
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if 0 <= item_id < len(items):
        deleted_item = items.pop(item_id)
        return {"deleted_item": deleted_item}
    else:
        raise HTTPException(status_code=404, detail="Item not found to delete")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)