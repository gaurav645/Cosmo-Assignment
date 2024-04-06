from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from bson import ObjectId
from pydantic import BaseModel  

app = FastAPI()

uri ="mongodb+srv://ramboon422:vZcM9srgFH5BvdXL@cluster0.4xqxalk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client["library"]
print("Connected to database")


class Book(BaseModel):
    title: str
    writer: str
    year: int

class BookNotFoundError(Exception):
    pass

@app.get("/books")
def get_all_books():
    books = list(db["books"].find({}, {"_id": 0}))  
    return {"books": books}
    

@app.post("/books")
def add_new_book(book_data: Book):
    result = db["books"].insert_one(book_data.dict())
    if result.inserted_id:
        return {"id": str(result.inserted_id)}
      
        
    else:
        raise HTTPException(status_code=500, detail="Failed to add book")


@app.put("/books/{book_id}")
def update_book(book_id: str, book_data: Book):
    result = db["books"].update_one({"_id": ObjectId(book_id)}, {"$set": book_data.dict()})
    if result.modified_count == 1:
        return {"message": "Book updated successfully"}
    else:
        raise BookNotFoundError(detail="Book not found")

#Exception handling

@app.exception_handler(BookNotFoundError)
async def book_not_found_exception_handler(request, exc):
    return JSONResponse(status_code=404, content={"error": "Book not found"})

@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    result = db["books"].delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return {"message": "Book deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Book not found")