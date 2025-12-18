from fastapi import status

from ..main import app
from ..routers.admin import get_db
from ..routers.auth import get_current_user
from ..models import Todos
from .utils import (
    client,
    override_get_db,
    override_get_current_user,
    TestingSessionLocal,
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated():
    db = TestingSessionLocal()
    todo = Todos(
        title="Learn to code",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    response = client.get("/auth/todo")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "id": todo.id,
        "title": "Learn to code",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False,
        "owner_id": 1,
    }]

def test_admin_delete_todo():
    db = TestingSessionLocal()
    todo = Todos(
        title="Learn to code",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    response = client.delete(f"/auth/todo/{todo.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    model = db.query(Todos).filter(Todos.id == todo.id).first()
    assert model is None


def test_admin_delete_todo():
    db = TestingSessionLocal()
    todo = Todos(
        title="Learn to code",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    response = client.delete(f"/auth/todo/{todo.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    model = db.query(Todos).filter(Todos.id == todo.id).first()
    assert model is None
