# Frontend Handout (React)

## Contents
- API.md (endpoints, schemas, curl)
- openapi.json (OpenAPI contract; use to generate types / SDK)
- .env.example (VITE_API_BASE_URL)

## Quick start
- Copy `.env.example` to `.env` and set the API base URL.
- Generate types or SDK from `openapi.json`.
- Consume endpoints as documented in `API.md` or live at `/docs`.

## Generate TypeScript types (Option A)
```bash
npx openapi-typescript ./openapi.json -o src/api/schema.ts
```

## Generate SDK (Option B)
```bash
npx @openapitools/openapi-generator-cli generate \
  -g typescript-fetch \
  -i ./openapi.json \
  -o src/api
```

## Environment
- `.env` in React project:
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Example usage (fetch)
```ts
const base = import.meta.env.VITE_API_BASE_URL;
const resp = await fetch(`${base}/todos/`);
const todos = await resp.json();
```
