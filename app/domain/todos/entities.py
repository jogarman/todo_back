from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TodoEntity:
    id: str
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
