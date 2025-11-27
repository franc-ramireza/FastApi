from datetime import date
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel , Field

import book

app = FastAPI()

class Book:
    id : int
    title : str
    author : str
    description: str
    rating : int
    publicated_date: int


    def __init__(self,id,title,author,description,rating, publicated_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.publicated_date = publicated_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default = None)
    title: str= Field(min_length=3)
    author: str= Field(min_length=1)
    description: str= Field(min_length=1, max_length=100)
    rating: int = Field(gt=0 , lt=6)
    publicated_date: int = Field(gt=1190, lt=2031)


    model_config = {
        "json_schema_extra": {
            "example":{
                "title": "A new book",
                "author": "Pedro Palacios",
                "description": "A new description of a book",
                "rating": 5,
                "publicated_date": 2012
            }
        }

    }


BOOKS = [
        Book(1, 'Computer Science Pro', 'Pepito', 'Very nice book ', 5, 2024),
        Book(2, 'Be fast with FastApi', 'Pepito', ' A great book ', 5,2012),
        Book(3, 'Master Endpoints', 'Pepito', 'A awesome book ', 5,2008),
        Book(4, 'HP1', 'Author 1', 'Book Description ', 2,1998),
        Book(5, 'HP2', 'Author 2', 'Book Description ', 3,2013),
        Book(6, 'HP3', 'Author 3', 'Book Description', 1,2025)
]

#Leertodosloslibros
@app.get("/books")
async def read_all_books():
    return BOOKS


#BuscarporAño
@app.get("/books/publicated_date/")
async def read_book_by_publicated_date(publicated_date: int):
    books_to_return = []
    for book in BOOKS:
        if book.publicated_date == publicated_date:
            books_to_return.append(book)
    return books_to_return


#Buscarporid
@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book

#BuscarporCalificacion
@app.get("/books/")
async def read_book_by_rating(book_rating: int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

#PostCrearlibro
@app.post("/create_book")
async def create_book(book_request : BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

def find_book_id(book:Book):
    if len(BOOKS) >0:
        book.id = BOOKS[-1].id+1

    else:
        book.id = 1
    return book

#ActualizarLibroFechaPublicacion
@app.put("/books/update_book")
async def update_book(book: BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i]= book


#EliminarunLibro
@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            break

