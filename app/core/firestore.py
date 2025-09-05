from __future__ import annotations

from typing import Optional
from google.cloud import firestore

from app.core.config import settings


_firestore_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    global _firestore_client
    if _firestore_client is None:
        if settings.gcp_project_id:
            _firestore_client = firestore.Client(project=settings.gcp_project_id)
        else:
            _firestore_client = firestore.Client()
    return _firestore_client
