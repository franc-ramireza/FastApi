from fastapi import Body , FastAPI
app = FastAPI()

BOOKS= [
    {'title':'Title One','author': 'Author One', 'category':'Science'},
    {'title':'Title Two','author': 'Author Two', 'category':'Science'},
    {'title':'Title Three','author':'Author Three', 'category':'History'},
    {'title':'Title Four','author': 'Author Four', 'category':'Math'},
    {'title':'Title Five','author': 'Author Five', 'category':'Math'},
    {'title':'Title Six','author': 'Author Two', 'category':'Math'}
]

#Buscatodolostitulos
@app.get("/books")
async def read_all_books():
    return BOOKS

#buscaportitulo
@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book

#buscaporcategoria
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

#buscarporautor
@app.get("/books/byauthor/")
async def read_books_by_author(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return

#buscaporautorycategoria
@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

#Crearunlibro
@app.post("/books/create_book")
async def create_book(new_book =Body()):
    BOOKS.append(new_book)

#Actualizarunlibro
@app.put("/books/update_book")
async def update_book(update_book =Body()):
    BOOKS.remove(update_book)
    for i in range (len(BOOKS)):
        if BOOKS[i].get('title').casefold() == update_book.get('title').casefold():
            BOOKS[i]= update_book

#Borrarlibro
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break

"""
Obtener todo los libros de un autor especifico , utilizando parametros de ruta o consulta 
crear un endpoint que tenga todos los libros de un autor especifico
"""


