from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


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


class FakeFirestoreClient:
    def __init__(self):
        self._collections: Dict[str, FakeCollection] = {}

    def collection(self, name: str) -> FakeCollection:
        if name not in self._collections:
            self._collections[name] = FakeCollection()
        return self._collections[name]


def test_crud_todos(monkeypatch):
    fake_db = FakeFirestoreClient()

    # Inyectar el cliente falso en el router
    import app.routers.todos as todos_router

    monkeypatch.setattr(todos_router, "get_firestore_client", lambda: fake_db)

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
