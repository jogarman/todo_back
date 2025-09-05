## Plan del Backend TODO SaaS

### Objetivo
Backend educativo para un servicio de TODOs (sin autenticación inicial) usando:
- **FastAPI (Python)**
- **Firestore (NoSQL)** en Firebase/Google Cloud
- **Poetry** para dependencias

### Alcance MVP (Fase 1)
- **CORS abierto** y endpoint **/health**
- **CRUD de todos**: listar, obtener, crear, actualizar, borrar
- **Configuración** por entorno con `pydantic-settings`
- **Cliente Firestore** con SDK oficial

### Arquitectura (carpetas/archivos)
- `app/main.py`: instancia FastAPI, CORS, health, include de routers
- `app/core/config.py`: settings desde `.env`
- `app/core/firestore.py`: cliente Firestore singleton
- `app/models/todo.py`: modelos Pydantic y mapeo Firestore
- `app/routers/todos.py`: rutas CRUD

### Modelo de datos (Firestore)
Colección: `todos`
Campos por documento:
- `title: string`
- `description?: string`
- `completed: boolean`
- `created_at: timestamp`
- `updated_at: timestamp`
Índice recomendado: `created_at` ascendente

### Entorno local
- Instalar deps: `poetry install`
- Ejecutar: `poetry run uvicorn app.main:app --reload`
- Variables opcionales en `.env`:
  - `GOOGLE_APPLICATION_CREDENTIALS` (ruta al JSON del service account)
  - `GCP_PROJECT_ID`

### Roadmap futuro
- Fase 2: Validaciones, manejo de errores homogéneo, logging estructurado
- Fase 3: Paginación, búsqueda y filtros en `/todos`
- Fase 4: Tests (pytest + httpx), cobertura básica y CI
- Fase 5: Autenticación (Google Identity Platform o JWT) [post-MVP]
- Fase 6: Versionado de API y documentación extendida OpenAPI

### Notas
- MVP sin auth para simplicidad
- CORS preparado para frontend React
