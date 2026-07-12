# API Contract Validator

Validates API endpoint implementations against `docs/api-contract.md`. Use when adding,
modifying, or reviewing HTTP routes, auth paths, CORS config, or frontend API client calls.

## When to Use

- Adding or changing routes in `apps/backend/` (or legacy `backend/`)
- M4 auth merge work — `/auth/*` on same host as `/api/v1/*`
- Frontend changes to API base URL or endpoint paths
- CORS or connectivity (H4) changes

## Spec Source

Primary: `docs/api-contract.md`
Secondary: `docs/guides/API.md`, `docs/deploy.md` §Integration

## Validation Checks

### 1. Endpoint existence

Every exposed route must appear in `docs/api-contract.md` §Endpoints:

| Path prefix | Service |
|-------------|---------|
| `GET /health` | Health check |
| `POST /auth/register` | Registration |
| `POST /auth/login` | Login |
| `POST /auth/logout` | Logout |
| `GET /auth/me` | Current user |
| `GET /auth/health` | Auth health |
| `POST /api/v1/convert` | Conversion (auth required) |
| `POST /api/v1/validate` | Validation |

Undocumented routes → `[Scope Drift]` unless back-added to api-contract.md.

### 2. Post-migration topology (M4)

- Auth and API share one host — no separate `:8003` service
- Frontend uses single `VITE_API_BASE_URL` for `/api/v1/*` and `/auth/*`
- docker-compose: two app services (backend, frontend), not three

### 3. Request/response shapes

- Conversion: multipart `files` + `manual_text` per contract
- Auth: Supabase JWT Bearer on protected routes
- `DISABLE_AUTH=true` — dev only, never production

### 4. CORS

- `METAR_CORS_ORIGINS` must include frontend origin
- `allow_methods` covers all browser-facing verbs (see `cors-browser-methods.mdc`)

## Output Format

```
API Contract Validation: PASS | FAIL

Findings:
- [endpoint] — status + spec section cite

Recommendations:
- ...
```

## State

Invoke **workflow-state-manager** `read_context` before validation when checking migration
task alignment. Log contradictions via agent `update` → `decisions_log`.
