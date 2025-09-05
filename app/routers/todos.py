from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException, Response
from google.cloud import firestore

from app.core.firestore import get_firestore_client
from app.models.todo import Todo, TodoCreate, TodoUpdate, now_utc, from_firestore_data

router = APIRouter(prefix="/todos", tags=["todos"])

COLLECTION = "todos"


@router.get("/", response_model=List[Todo])
def list_todos() -> List[Todo]:
    db = get_firestore_client()
    docs = (
        db.collection(COLLECTION)
        .order_by("created_at", direction=firestore.Query.ASCENDING)
        .stream()
    )
    return [from_firestore_data(doc.id, doc.to_dict()) for doc in docs]


@router.get("/{todo_id}", response_model=Todo)
def get_todo(todo_id: str) -> Todo:
    db = get_firestore_client()
    snap = db.collection(COLLECTION).document(todo_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Todo not found")
    return from_firestore_data(snap.id, snap.to_dict())


@router.post("/", response_model=Todo, status_code=201)
def create_todo(payload: TodoCreate) -> Todo:
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION).document()
    now = now_utc()
    data = {
        "title": payload.title,
        "description": payload.description,
        "completed": payload.completed,
        "created_at": now,
        "updated_at": now,
    }
    doc_ref.set(data)
    return from_firestore_data(doc_ref.id, data)


@router.put("/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, payload: TodoUpdate) -> Todo:
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION).document(todo_id)
    snap = doc_ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Todo not found")

    current = snap.to_dict()
    updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    updates["updated_at"] = now_utc()
    doc_ref.update(updates)

    current.update(updates)
    return from_firestore_data(todo_id, current)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: str) -> Response:
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION).document(todo_id)
    snap = doc_ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Todo not found")
    doc_ref.delete()
    return Response(status_code=204)
