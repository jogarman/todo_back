from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from app.repositories.todos.firestore_repository import FirestoreTodoRepository
from app.schemas.todos import TodoCreate, TodoUpdate, TodoRead
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


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: str, service: TodoService = Depends(get_todo_service)) -> TodoRead:
    entity = service.get_todo(todo_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return TodoRead(**entity.__dict__)


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
