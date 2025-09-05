from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from fastapi.testclient import TestClient
from fastapi import Depends

from app.api.routers import todos as todos_router
from app.services.todos.service import TodoService
from app.domain.todos.entities import TodoEntity
from app.domain.todos.interfaces import TodoRepository


class FakeDocumentSnapshot:
    def __init__(self, doc_id: str, data: Dict[str, Any]):
        self.id = doc_id
        self._data = data
        self.exists = True

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


class FakeDocumentRef:
    def __init__(self, collection: "FakeCollection", doc_id: str):
        self._collection = collection
        self.id = doc_id

    def get(self) -> FakeDocumentSnapshot:
        data = self._collection._store.get(self.id)
        if data is None:
            snap = FakeDocumentSnapshot(self.id, {})
            snap.exists = False
            return snap
        return FakeDocumentSnapshot(self.id, data)

    def set(self, data: Dict[str, Any]) -> None:
        self._collection._store[self.id] = dict(data)

    def update(self, data: Dict[str, Any]) -> None:
        current = self._collection._store.get(self.id, {})
        current.update(data)
        self._collection._store[self.id] = current

    def delete(self) -> None:
        self._collection._store.pop(self.id, None)


class FakeQuery:
    def __init__(self, collection: "FakeCollection"):
        self._collection = collection

    def stream(self) -> List[FakeDocumentSnapshot]:
        docs = [
            FakeDocumentSnapshot(doc_id, data)
            for doc_id, data in self._collection._store.items()
        ]
        docs.sort(key=lambda d: d.to_dict().get("created_at", datetime(1970, 1, 1, tzinfo=timezone.utc)))
        return docs


class FakeCollection:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def document(self, doc_id: Optional[str] = None) -> FakeDocumentRef:
        if doc_id is None:
            doc_id = uuid4().hex
        return FakeDocumentRef(self, doc_id)

    def order_by(self, *args: Any, **kwargs: Any) -> FakeQuery:
        return FakeQuery(self)


class InMemoryTodoRepository(TodoRepository):
    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def list(self) -> List[TodoEntity]:
        docs = [
            TodoEntity(
                id=doc_id,
                title=data["title"],
                description=data.get("description"),
                completed=bool(data.get("completed", False)),
                created_at=data["created_at"],
                updated_at=data["updated_at"],
            )
            for doc_id, data in self._store.items()
        ]
        docs.sort(key=lambda e: e.created_at)
        return docs

    def get(self, todo_id: str) -> TodoEntity | None:
        data = self._store.get(todo_id)
        if data is None:
            return None
        return TodoEntity(
            id=todo_id,
            title=data["title"],
            description=data.get("description"),
            completed=bool(data.get("completed", False)),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def create(self, title: str, description: str | None, completed: bool, now) -> TodoEntity:
        doc_id = uuid4().hex
        data = {
            "title": title,
            "description": description,
            "completed": completed,
            "created_at": now,
            "updated_at": now,
        }
        self._store[doc_id] = data
        return self.get(doc_id)  # type: ignore[return-value]

    def update(self, todo_id: str, updates: dict, now) -> TodoEntity | None:
        if todo_id not in self._store:
            return None
        current = self._store[todo_id]
        current.update(updates)
        current["updated_at"] = now
        self._store[todo_id] = current
        return self.get(todo_id)

    def delete(self, todo_id: str) -> bool:
        return self._store.pop(todo_id, None) is not None


def test_crud_todos(monkeypatch):
    # Use a single in-memory repository instance shared across requests
    shared_repo = InMemoryTodoRepository()
    shared_service = TodoService(repository=shared_repo)

    # Override dependency to inject the shared service
    def get_test_service() -> TodoService:
        return shared_service

    app.dependency_overrides[todos_router.get_todo_service] = get_test_service
    client = TestClient(app)

    # List inicial vacío
    resp = client.get("/todos/")
    assert resp.status_code == 200
    assert resp.json() == []

    # Crear
    payload = {"title": "Aprender FastAPI", "description": "Hacer un CRUD", "completed": False}
    resp = client.post("/todos/", json=payload)
    assert resp.status_code == 201
    created = resp.json()
    assert created["title"] == payload["title"]
    assert created["completed"] is False
    assert isinstance(created["id"], str)

    todo_id = created["id"]

    # Obtener por id
    resp = client.get(f"/todos/{todo_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == todo_id

    # Actualizar
    resp = client.put(f"/todos/{todo_id}", json={"completed": True})
    assert resp.status_code == 200
    assert resp.json()["completed"] is True

    # Listar debería contener 1
    resp = client.get("/todos/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Borrar
    resp = client.delete(f"/todos/{todo_id}")
    assert resp.status_code == 204

    # Obtener tras borrar => 404
    resp = client.get(f"/todos/{todo_id}")
    assert resp.status_code == 404
