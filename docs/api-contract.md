# API Contract

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-07-12 (S008 F6 delta)
> **Delta**: Monorepo migration M4 — auth merged; F6 tac2iwxxm convert product/profile

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
  "tac2iwxxm_available": true
}
```

**Breaking (F6 cutover)**: `gifts_available` removed; clients must use `tac2iwxxm_available`.
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

**Auth**: Required unless `DISABLE_AUTH=true` (dev only). Guests may convert when that policy applies;
work-session persistence still requires JWT.

**Request** (multipart/form-data **only** for product/profile — not read from JSON body):

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `files` | no* | — | TAC files |
| `manual_text` | no* | — | TAC string |
| `product` | **yes** | — | `airmet` \| `metar` \| `sigmet` \| `speci` \| `taf` \| `vaa` \| `tca` |
| `profile` | no | `annex3` | `annex3` \| `iwxxm_us` |
| `iwxxm_version` | no | app default | Vendored pin (e.g. `2025-2`) |

\* At least one of `files` or `manual_text` required (unchanged).

**Notes**:
- Auto-detect is **UI-side only**; API rejects missing `product` with **400**.
- F5 may **store** `product`/`profile` in `conversion_params` for UI restore; on submit the UI
  **copies** them into multipart fields.
- No `engine` field; converter is always `tac2iwxxm` after cutover.
- No metrics object on the response (library/CI only).

**Response**: `ConversionResponse` — see docs/guides/API.md (shape unchanged).

Each `ConversionResult` includes optional `tac_input` (original TAC echo) for input traceability ([#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594)).

**Errors** (F6): Prefer existing `errors` / `issues` arrays; include machine-readable `code` when applicable:

| code | HTTP | When |
|------|------|------|
| `unknown_product` | 400 | Invalid product enum / unsupported |
| `invalid_profile` | 400 | Profile not in enum |
| `missing_iwxxm_us` | 400 | `profile=iwxxm_us` but vendor pin/catalog missing |
| `parse_failed` | 422 | TAC fails product parse |

Unexpected converter crashes remain **5xx**.

### Validation

```
POST /api/v1/validate
```

**Request**: Existing body/content-type **plus** optional `profile` (`annex3` default |
`iwxxm_us`). When US, validation uses combined WMO + iwxxm-us catalogs.

**Response**: Unchanged pass/fail + messages shape.
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
  "conversion_params": { "iwxxm_version": "2025-2", "product": "metar", "profile": "annex3" },
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

F6 product/profile fields do **not** change CORS headers. Frontend and API remain different
origins on Render; configure `config.*.api.corsOrigins` accordingly.

## Error Format

```json
{
  "detail": "Human-readable message"
}
```

Convert responses may also carry `errors` / `issues` with optional `code` (see Conversion).
HTTP status codes: 400 / 422 / 5xx as documented for F6; other routes unchanged.

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

**Breaking changes (F6 cutover)**:
- Health: `gifts_available` → `tac2iwxxm_available`
- Convert: `product` required; `profile` optional (default `annex3`); multipart-only for those fields
- No gifts dual-run / no `engine` parameter

OpenAPI / shared TS codegen remains planned (P1); this contract is the requirements SoT until then.

## References

- docs/guides/API.md (detailed examples — update paths during implementation)
- docs/deploy.md §Integration
- ADR-014

### Session changelog

- S008 (2026-07-12): product required; profile; tac2iwxxm_available; validate profile; error codes
