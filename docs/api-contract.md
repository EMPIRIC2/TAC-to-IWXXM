# API Contract

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-06-14
> **Delta**: Monorepo migration M4 — auth service merged into backend API

## Base URLs

| Environment | Frontend | API (includes auth) |
|-------------|----------|---------------------|
| Local dev | `http://localhost:18000` | `http://localhost:18001` |
| Render | `https://<frontend-host>` | `https://<api-host>` |

**Post-migration change**: Auth endpoints move from separate `:8003` service to same host as backend.
Frontend uses single `VITE_API_BASE_URL` for both `/api/v1/*` and `/auth/*`.

## Services

| Service | Pre-migration | Post-migration |
|---------|---------------|----------------|
| Conversion API | backend:8001 | apps/backend |
| Auth | auth:8003 | apps/backend (packages/auth) |
| Frontend | frontend:5173/8000 | apps/frontend |

## Endpoints

### Health

```
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "gifts_available": true
}
```

### Authentication (packages/auth — same host post-migration)

```
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
GET  /auth/health
```

**Auth**: Supabase JWT; Bearer token on protected routes.

**Migration note**: Paths preserved for frontend compatibility; proxy config simplified.

### Conversion

```
POST /api/v1/convert
```

**Auth**: Required unless `DISABLE_AUTH=true` (dev only).

**Request** (multipart/form-data):
- `files` (optional): METAR TAC files
- `manual_text` (optional): TAC string

**Response**: `ConversionResponse` — see docs/API.md

### Validation

```
POST /api/v1/validate
```

**Request/Response**: Unchanged from current backend contract.

## CORS

| Header | Value |
|--------|-------|
| `Access-Control-Allow-Origin` | Origins from `METAR_CORS_ORIGINS` |
| `Access-Control-Allow-Methods` | GET, POST, OPTIONS |
| `Access-Control-Allow-Headers` | Authorization, Content-Type |

Preflight: `OPTIONS` on `/api/v1/*` and `/auth/*`.

## Error Format

```json
{
  "detail": "Human-readable message"
}
```

HTTP status codes unchanged.

## Frontend Integration

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE_URL` | API + auth base (post-migration unified) |
| `VITE_SUPABASE_URL` | Supabase project (client-side anon) |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | Supabase anon key |

**Breaking changes**: None intended for public JSON shapes. Internal Docker service names change
(`auth:8000` → in-process).

## References

- docs/API.md (detailed examples — update paths during implementation)
- docs/deploy.md §Integration
