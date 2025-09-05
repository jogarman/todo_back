from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    completed: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Todo(TodoBase):
    id: str
    created_at: datetime
    updated_at: datetime


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_firestore_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    return payload


def from_firestore_data(doc_id: str, data: Dict[str, Any]) -> Todo:
    return Todo(
        id=doc_id,
        title=data.get("title", ""),
        description=data.get("description"),
        completed=bool(data.get("completed", False)),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )
