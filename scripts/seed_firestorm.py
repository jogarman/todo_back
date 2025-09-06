from __future__ import annotations

from datetime import datetime, timezone

from app.core.firestore import get_firestore_client


def main():
    db = get_firestore_client()
    coll = db.collection("todos")
    now = datetime.now(timezone.utc)
    samples = [
        {"title": "Sample A", "description": None, "completed": False, "created_at": now, "updated_at": now},
        {"title": "Sample B", "description": "desc", "completed": True, "created_at": now, "updated_at": now},
    ]
    for s in samples:
        coll.add(s)
    print("Seeded", len(samples), "todos")


if __name__ == "__main__":
    main()
