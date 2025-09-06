# TODO SaaS Backend

Backend en Python con FastAPI y Firestore (Google Cloud). Gestión de dependencias con Poetry.

## Requisitos
- Poetry
- Python 3.10+
- Credenciales de Google Cloud para Firestore (opcional para arrancar el servidor)

## Variables de entorno
- `TODO_GCP_PROJECT_ID` (o `GCP_PROJECT_ID`)
- `TODO_GOOGLE_APPLICATION_CREDENTIALS` (o `GOOGLE_APPLICATION_CREDENTIALS`)

Ejemplo local seguro:
```
mkdir -p ~/.secrets
mv /ruta/al/service-account.json ~/.secrets/todo-ddbb-sa.json
chmod 600 ~/.secrets/todo-ddbb-sa.json
export TODO_GOOGLE_APPLICATION_CREDENTIALS="$HOME/.secrets/todo-ddbb-sa.json"
export TODO_GCP_PROJECT_ID="todo-ddbb"
```

## Desarrollo
- Instalar dependencias: `poetry install`
- Ejecutar servidor: `poetry run uvicorn app.main:app --reload`
- Variables de entorno: ver sección anterior o `.env`
