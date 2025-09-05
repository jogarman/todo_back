from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import List, Protocol

from app.domain.todos.entities import TodoEntity


class TodoRepository(Protocol):
    def list(self) -> List[TodoEntity]:
        ...

    def get(self, todo_id: str) -> TodoEntity | None:
        ...

    def create(self, title: str, description: str | None, completed: bool, now: datetime) -> TodoEntity:
        ...

    def update(self, todo_id: str, updates: dict, now: datetime) -> TodoEntity | None:
        ...

    def delete(self, todo_id: str) -> bool:
        ...


def entity_to_dict(entity: TodoEntity) -> dict:
    # Helper to convert entity to plain dict if ever needed
    return asdict(entity)
