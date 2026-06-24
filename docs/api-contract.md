# API Contract

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-06-23 (F5 work history delta) (S003 Supabase keys + runtime config)
> **Delta**: Monorepo migration M4 — auth service merged into backend API

## Base URLs

| Environment | Frontend | API (includes auth) |
|-------------|----------|---------------------|
| Local dev | `http://localhost:18000` | `http://localhost:18001` |
| Render | `https://<frontend-host>` | `https://<api-host>` |

**Post-migration change**: Auth endpoints move from separate `:8003` service to same host as backend.
Frontend uses single `VITE_API_BASE_URL` for `/api/v1/*`, `/auth/*`, and `/admin/*`.

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

### Admin (packages/auth — same host post-migration)

```
GET  /admin/settings
POST /admin/settings
GET  /admin/all-users
GET  /admin/stats
POST /admin/toggle-admin
```

**Auth**: Supabase JWT; Bearer token required. Caller must have `user_profiles.is_admin = true`.
Server uses the caller's JWT with **publishable key** + existing RLS policies (`is_admin()`).
`SUPABASE_SECRET_KEY` is **not** used for routine admin routes — reserved for Auth Admin API
scripts only (ADR-010).

**Note**: Settings are stored in-process (not durable across deploys); see PR #679.

### Conversion

```
POST /api/v1/convert
```

**Auth**: Required unless `DISABLE_AUTH=true` (dev only).

**Request** (multipart/form-data):
- `files` (optional): METAR TAC files
- `manual_text` (optional): TAC string

**Response**: `ConversionResponse` — see docs/API.md

Each `ConversionResult` includes optional `tac_input` (original TAC echo) for input traceability ([#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594)).

### Validation

```
POST /api/v1/validate
```

**Request/Response**: Unchanged from current backend contract.

### Work sessions (F5 — S004 / EV-004)

All routes require Bearer JWT unless noted. User routes enforce RLS via caller JWT.

```
GET    /api/v1/work-sessions
POST   /api/v1/work-sessions
GET    /api/v1/work-sessions/{id}
PATCH  /api/v1/work-sessions/{id}
DELETE /api/v1/work-sessions/{id}
POST   /api/v1/work-sessions/{id}/restore
```

**Query params** (`GET` list): `status`, `from`, `to`, `include_deleted` (trash view), `page`, `limit`.

**Request body** (`POST` / `PATCH`):

```json
{
  "title": "optional — default auto ICAO + timestamp",
  "manual_tac": "string",
  "pending_files": [{ "name": "file.tac", "content": "METAR ..." }],
  "converted_results": [],
  "errors": [],
  "issues": [],
  "conversion_params": { "iwxxm_version": "2025-2" },
  "status": "draft | wip | finished | failed",
  "kv_upload_key": "optional — set on successful send"
}
```

**Response** (`WorkSession`):

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "status": "draft",
  "title": "KJFK 2026-06-23",
  "manual_tac": "...",
  "pending_files": [],
  "converted_results": [],
  "errors": [],
  "issues": [],
  "conversion_params": {},
  "kv_upload_key": null,
  "deleted_at": null,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Status transitions** (server-enforced):

| From | Event | To |
|------|-------|-----|
| — | Auto-save / create | draft |
| draft / failed | Convert success (no send) | wip (reject if another wip exists) |
| draft / failed | Convert failure | failed |
| wip | Send success | finished (+ kv_upload_key) |
| wip | Send failure | wip (unchanged — user may retry) |
| any | User soft-delete | deleted_at set |
| deleted | Restore within 30 days | deleted_at cleared |

**Admin** (read-only, `is_admin()`):

```
GET /admin/work-sessions
```

Same list shape with `user_email` or profile fields; no mutate endpoints in v1.

**Admin UI**: Dedicated admin page consumes this endpoint; not a toggle on My METARs.

**Guest users**: Work-session routes require JWT. Unauthenticated users may call `/api/v1/convert`
but receive no session persistence until login. On first authenticated request after login, if the
frontend holds unsaved converter state, it **POST**s a new **draft** session from that state before
resume logic runs.

## CORS

| Header | Value |
|--------|-------|
| `Access-Control-Allow-Origin` | Origins from `config.*.api.corsOrigins` |
| `Access-Control-Allow-Methods` | GET, POST, OPTIONS |
| `Access-Control-Allow-Headers` | Authorization, Content-Type |

Preflight: `OPTIONS` on `/api/v1/*`, `/auth/*`, and `/admin/*`.

## Error Format

```json
{
  "detail": "Human-readable message"
}
```

HTTP status codes unchanged.

## Frontend Integration

Runtime config via `GET /config.json` (copied from `config/prod.json` at deploy; publishable
key injected from `SUPABASE_PUBLISHABLE_KEY`).

| Config field | Purpose |
|--------------|---------|
| `api.baseUrl` | API + auth base (`/api/v1`, `/auth`, `/admin`) |
| `supabase.url` | Supabase project URL |
| `supabase.publishableKey` | Client-side Supabase auth (injected at deploy) |

**Deprecated**: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`,
`VITE_APP_URL` — one-release shim during S003 migration.

**Breaking changes**: None intended for public JSON shapes. Internal Docker service names change
(`auth:8000` → in-process).

## References

- docs/API.md (detailed examples — update paths during implementation)
- docs/deploy.md §Integration
