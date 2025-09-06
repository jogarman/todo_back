from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response

from app.repositories.todos.firestore_repository import FirestoreTodoRepository
from app.schemas.todos import TodoCreate, TodoUpdate, TodoRead, TodoPage
from app.services.todos.service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


# Dependency factory: swap this for another repository in tests or other envs

def get_todo_service() -> TodoService:
    repository = FirestoreTodoRepository()
    return TodoService(repository=repository)


@router.get("/", response_model=List[TodoRead])
def list_todos(service: TodoService = Depends(get_todo_service)) -> List[TodoRead]:
    entities = service.list_todos()
    return [
        TodoRead(
            id=e.id,
            title=e.title,
            description=e.description,
            completed=e.completed,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        for e in entities
    ]


@router.get("/paged", response_model=TodoPage)
def list_todos_paged(
    limit: int = 20,
    completed: Optional[bool] = None,
    after: Optional[str] = None,
    service: TodoService = Depends(get_todo_service),
) -> TodoPage:
    # Simple in-memory pagination leveraging existing list (for demo). For large datasets, use Firestore cursors.
    items = [
        TodoRead(
            id=e.id,
            title=e.title,
            description=e.description,
            completed=e.completed,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        for e in service.list_todos()
    ]
    if completed is not None:
        items = [i for i in items if i.completed == completed]
    # Cursor by ISO datetime of created_at
    start_index = 0
    if after:
        try:
            from datetime import datetime

            cursor_dt = datetime.fromisoformat(after.replace("Z", "+00:00"))
            for idx, i in enumerate(items):
                if i.created_at > cursor_dt:
                    start_index = idx
                    break
        except Exception:
            start_index = 0
    page = items[start_index : start_index + max(1, min(100, limit))]
    next_cursor = page[-1].created_at if len(page) == max(1, min(100, limit)) else None
    return TodoPage(items=page, next_cursor=next_cursor)


@router.post("/", response_model=TodoRead, status_code=201)
def create_todo(payload: TodoCreate, service: TodoService = Depends(get_todo_service)) -> TodoRead:
    entity = service.create_todo(title=payload.title, description=payload.description, completed=payload.completed)
    return TodoRead(**entity.__dict__)


@router.put("/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: str, payload: TodoUpdate, service: TodoService = Depends(get_todo_service)) -> TodoRead:
    updates = payload.model_dump(exclude_unset=True)
    entity = service.update_todo(todo_id=todo_id, updates=updates)
    if entity is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoRead(**entity.__dict__)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: str, service: TodoService = Depends(get_todo_service)) -> Response:
    deleted = service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return Response(status_code=204)


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: str, service: TodoService = Depends(get_todo_service)) -> TodoRead:
    entity = service.get_todo(todo_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoRead(**entity.__dict__)
