# TODO SaaS Backend

Backend en Python con FastAPI y Firestore (Google Cloud). Gestión de dependencias con Poetry.

## Requisitos
- Poetry
- Python 3.10+
- Credenciales de Google Cloud para Firestore (opcional para arrancar el servidor)

## Desarrollo
- Instalar dependencias: `poetry install`
- Ejecutar servidor: `poetry run uvicorn app.main:app --reload`
- Variables de entorno: ver `.env.example`
