from __future__ import annotations

from app.core.firestore import get_firestore_client


def main():
    db = get_firestore_client()
    coll = db.collection("todos")
    count = 0
    for doc in coll.stream():
        doc.reference.delete()
        count += 1
    print("Deleted", count, "todos")


if __name__ == "__main__":
    main()
