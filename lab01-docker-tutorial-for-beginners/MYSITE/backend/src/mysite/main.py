import os
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# Load MongoDB connection string from environment variable
MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]

# Connect to MongoDB using Motor (async driver)
client = AsyncIOMotorClient(MONGODB_CONNECTION_STRING, uuidRepresentation="standard")
db = client.todolist
todos = db.todos

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend running on localhost
# if you forget to add the CORS middleware the browser will block the requests 
# we access the website from Local Host on Port 80 but the JavaScript is calling Local Host on Port 8000
# for security purposes those are treated as two completely different websites 
# browser treates that as malicious behaviour and blocks it unless the respons specifcally indicates that it's okay

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data model for a to-do item: id and a content
class TodoItem(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    content: str

# Define the model for creating a new to-do item: only content needed
class TodoItemCreate(BaseModel):
    content: str

# 3 endpoints:
## to create to-do items
@app.post("/todos", response_model=TodoItem)
async def create_todo(item: TodoItemCreate):
    new_todo = TodoItem(content=item.content)
    await todos.insert_one(new_todo.model_dump(by_alias=True))
    return new_todo

# to retrieve all to-do items
@app.get("/todos", response_model=list[TodoItem])
async def read_todos():
    return await todos.find().to_list(length=None)

# to delete to-do item by it's UUID
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: UUID):
    delete_result = await todos.delete_one({"_id": todo_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}

# Run the app using Uvicorn when executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)