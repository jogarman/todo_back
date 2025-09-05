from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    # Input schema used when creating a Todo
    title: str = Field(min_length=1)
    description: Optional[str] = None
    completed: bool = False


class TodoUpdate(BaseModel):
    # Input schema for partial updates
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoRead(BaseModel):
    # Output schema returned to clients
    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime
