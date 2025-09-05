from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers.todos import router as todos_router
from app.middlewares.request_id import RequestIdMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware

app = FastAPI(title="TODO SaaS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add basic middlewares for observability and security
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}


app.include_router(todos_router)
