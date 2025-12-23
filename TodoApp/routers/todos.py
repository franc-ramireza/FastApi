from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Request,
    status,
)
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from ..database import get_db
from ..models import Todos
from .auth import get_current_user, SECRET_KEY, ALGORITHM


# =======================
# SETUP
# =======================

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

templates = Jinja2Templates(directory="TodoApp/templates")

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# =======================
# MODELS
# =======================

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


# =======================
# HELPERS
# =======================

def redirect_to_login():
    response = RedirectResponse(
        url="/auth/login-page",
        status_code=status.HTTP_302_FOUND,
    )
    response.delete_cookie("access_token")
    return response


def get_current_user_from_cookie(token: str | None):
    if token is None:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "user_id": payload.get("id"),
            "username": payload.get("sub"),
            "role": payload.get("role"),
        }
    except JWTError:
        return None


# =======================
# PAGES (WEB – COOKIE AUTH)
# =======================

@router.get("/todo-page")
def render_todo_page(request: Request, db: db_dependency):
    user = get_current_user_from_cookie(
        request.cookies.get("access_token")
    )

    if user is None:
        return redirect_to_login()

    todos = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("user_id"))
        .all()
    )

    return templates.TemplateResponse(
        "todos.html",
        {
            "request": request,
            "todos": todos,
            "user": user,
        },
    )


@router.get("/add-todo-page")
def render_add_todo_page(request: Request):
    user = get_current_user_from_cookie(
        request.cookies.get("access_token")
    )

    if user is None:
        return redirect_to_login()

    return templates.TemplateResponse(
        "add-todo.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.get("/edit-todo-page/{todo_id}")
def render_edit_todo_page(
    request: Request,
    db: db_dependency,
    todo_id: int = Path(gt=0),
):
    user = get_current_user_from_cookie(
        request.cookies.get("access_token")
    )

    if user is None:
        return redirect_to_login()

    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("user_id"))
        .first()
    )

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return templates.TemplateResponse(
        "edit-todo.html",
        {
            "request": request,
            "todo": todo,
            "user": user,
        },
    )


# =======================
# WEB POSTS (COOKIE AUTH)
# =======================

@router.post("/todo/web", status_code=status.HTTP_201_CREATED)
def create_todo_from_web(
    request: Request,
    db: db_dependency,
    todo_request: TodoRequest,
):
    user = get_current_user_from_cookie(
        request.cookies.get("access_token")
    )

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo = Todos(
        **todo_request.model_dump(),
        owner_id=user.get("user_id"),
    )

    db.add(todo)
    db.commit()


@router.post("/edit-todo/web/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo_from_web(
    request: Request,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    user = get_current_user_from_cookie(
        request.cookies.get("access_token")
    )

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("user_id"))
        .first()
    )

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete

    db.commit()


@router.post("/delete-todo/web/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_from_web(
    request: Request,
    db: db_dependency,
    todo_id: int = Path(gt=0),
):
    user = get_current_user_from_cookie(
        request.cookies.get("access_token")
    )

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    todo = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("user_id"))
        .first()
    )

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()


# =======================
# API (OAUTH2 – HEADER AUTH)
# =======================

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401)

    return (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("user_id"))
        .all()
    )


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo_api(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
):
    if user is None:
        raise HTTPException(status_code=401)

    todo = Todos(
        **todo_request.model_dump(),
        owner_id=user.get("user_id"),
    )

    db.add(todo)
    db.commit()
