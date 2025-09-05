from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.domain.todos.entities import TodoEntity
from app.domain.todos.interfaces import TodoRepository


class TodoService:
    def __init__(self, repository: TodoRepository) -> None:
        self._repository = repository

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def list_todos(self) -> List[TodoEntity]:
        return self._repository.list()

    def get_todo(self, todo_id: str) -> TodoEntity | None:
        return self._repository.get(todo_id)

    def create_todo(self, title: str, description: str | None, completed: bool) -> TodoEntity:
        return self._repository.create(title=title, description=description, completed=completed, now=self._now())

    def update_todo(self, todo_id: str, updates: dict) -> TodoEntity | None:
        return self._repository.update(todo_id=todo_id, updates=updates, now=self._now())

    def delete_todo(self, todo_id: str) -> bool:
        return self._repository.delete(todo_id)
