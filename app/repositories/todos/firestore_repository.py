from __future__ import annotations

from datetime import datetime
from typing import List

from google.cloud import firestore

from app.core.firestore import get_firestore_client
from app.domain.todos.entities import TodoEntity
from app.domain.todos.interfaces import TodoRepository


_COLLECTION = "todos"


def _doc_to_entity(doc: firestore.DocumentSnapshot) -> TodoEntity:
    data = doc.to_dict() or {}
    return TodoEntity(
        id=doc.id,
        title=data.get("title", ""),
        description=data.get("description"),
        completed=bool(data.get("completed", False)),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )


class FirestoreTodoRepository(TodoRepository):
    def __init__(self, client: firestore.Client | None = None) -> None:
        self._client = client or get_firestore_client()

    @property
    def _collection(self) -> firestore.CollectionReference:
        return self._client.collection(_COLLECTION)

    def list(self) -> List[TodoEntity]:
        docs = (
            self._collection
            .order_by("created_at", direction=firestore.Query.ASCENDING)
            .stream()
        )
        return [_doc_to_entity(doc) for doc in docs]

    def get(self, todo_id: str) -> TodoEntity | None:
        snap = self._collection.document(todo_id).get()
        if not snap.exists:
            return None
        return _doc_to_entity(snap)

    def create(self, title: str, description: str | None, completed: bool, now: datetime) -> TodoEntity:
        doc_ref = self._collection.document()
        data = {
            "title": title,
            "description": description,
            "completed": completed,
            "created_at": now,
            "updated_at": now,
        }
        doc_ref.set(data)
        return TodoEntity(
            id=doc_ref.id,
            title=title,
            description=description,
            completed=completed,
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def update(self, todo_id: str, updates: dict, now: datetime) -> TodoEntity | None:
        doc_ref = self._collection.document(todo_id)
        snap = doc_ref.get()
        if not snap.exists:
            return None
        updates = dict(updates)
        updates["updated_at"] = now
        doc_ref.update(updates)
        current = snap.to_dict() or {}
        current.update(updates)
        return TodoEntity(
            id=todo_id,
            title=current.get("title", ""),
            description=current.get("description"),
            completed=bool(current.get("completed", False)),
            created_at=current.get("created_at"),
            updated_at=current.get("updated_at"),
        )

    def delete(self, todo_id: str) -> bool:
        doc_ref = self._collection.document(todo_id)
        if not doc_ref.get().exists:
            return False
        doc_ref.delete()
        return True
