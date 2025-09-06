# API Reference

Base URL (dev): `http://127.0.0.1:8000`

OpenAPI/Swagger: `/docs`  ·  ReDoc: `/redoc`  ·  JSON: `/openapi.json`

## Health
GET `/health`
- 200: `{ "status": "ok", "env": "development" }`

## Todos

### List
GET `/todos/`
- 200: `TodoRead[]`

cURL:
```
curl -s http://127.0.0.1:8000/todos/
```

### List (paged)
GET `/todos/paged`
- Query:
  - `limit` (int, default 20, max 100)
  - `completed` (bool, optional)
  - `after` (ISO datetime cursor, opcional)
- 200: `{ items: TodoRead[], next_cursor: string|null }`

cURL:
```
curl -s "http://127.0.0.1:8000/todos/paged?limit=10"
```

### Get by id
GET `/todos/{id}`
- 200: `TodoRead`
- 404: `{ "detail": "Todo not found" }`

### Create
POST `/todos/`
- Body `TodoCreate`:
```
{
  "title": "string",
  "description": "string|null",
  "completed": false
}
```
- 201: `TodoRead`
- 422: validation error

cURL:
```
curl -s -X POST http://127.0.0.1:8000/todos/ \
  -H 'Content-Type: application/json' \
  -d '{"title":"Learn","description":null,"completed":false}'
```

### Update
PUT `/todos/{id}`
- Body `TodoUpdate` (parcial):
```
{
  "title": "string?",
  "description": "string?",
  "completed": true?
}
```
- 200: `TodoRead`
- 404: `{ "detail": "Todo not found" }`

### Delete
DELETE `/todos/{id}`
- 204: sin cuerpo
- 404: `{ "detail": "Todo not found" }`

## Schemas
- `TodoRead`:
```
{
  "id": "string",
  "title": "string",
  "description": "string|null",
  "completed": bool,
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```
- `TodoCreate`: `{ title: string, description?: string|null, completed?: bool }`
- `TodoUpdate`: `{ title?: string, description?: string|null, completed?: bool }`

## Headers y CORS
- `X-Request-ID` se agrega automáticamente a la respuesta.
- CORS está habilitado (config por entorno). En dev se permite `*`.

## Entorno
- `TODO_GCP_PROJECT_ID` y `TODO_GOOGLE_APPLICATION_CREDENTIALS` para Firestore.
