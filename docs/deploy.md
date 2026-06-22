# Deployment

> **Project**: METAR to IWXXM Converter
> **Platform**: Render (Docker web service + static site)
> **Last updated**: 2026-06-22

## Topology (post-monorepo)

| Service | Type | Source | Port |
|---------|------|--------|------|
| metar-api | Web (Docker) | `apps/backend` Dockerfile | `$PORT` (0.0.0.0) |
| metar-frontend | **Static site** (CDN) | `apps/frontend` Vite build | CDN |

Auth is **not** a separate deployable — included in metar-api via packages/auth.

**Observability**: Render built-in logs only — Loki/Prometheus/Grafana removed from Blueprint (ADR-006).

## Integration

### Build-time (frontend)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes | HTTPS URL of metar-api service |
| `VITE_SUPABASE_URL` | Yes | Supabase project URL |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | Yes | Supabase anon key |
| `VITE_APP_URL` | Yes | Public frontend URL (redirects) |

### Runtime (API)

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Server-side Supabase |
| `SUPABASE_ANON_KEY` | Yes | Server-side validation |
| `METAR_CORS_ORIGINS` | Yes | Comma-separated frontend origin(s) — see [staging-secrets-matrix.md](staging-secrets-matrix.md) |
| `DISABLE_AUTH` | No | `false` in production (ADR-006) |
| `FRONTEND_URL` | Yes | For redirects / CORS |

### Live test env (manual T3 runs)

| Variable | Required | Description |
|----------|----------|-------------|
| `LIVE_API_URL` | Yes | `https://metar-to-iwxxm-api.onrender.com` |
| `LIVE_FRONTEND_URL` | Yes | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` |
| `PLAYWRIGHT_BASE_URL` | Yes (H6) | Same as `LIVE_FRONTEND_URL` for Playwright |
| `ADMIN_EMAIL` | Yes (H6) | Supabase admin user — local `.env` only, never commit |
| `ADMIN_PASSWORD` | Yes (H6) | Supabase admin password — local `.env` only |

**Deprecated aliases** (migrate scripts/tests away from):

| Old name | Replaced by |
|----------|-------------|
| `STAGING_API_URL` | `LIVE_API_URL` |
| `STAGING_FRONTEND_ORIGIN` | `LIVE_FRONTEND_URL` |
| `STAGING_FRONTEND_URL` | `LIVE_FRONTEND_URL` |
| `E2E_API_URL` | `LIVE_API_URL` |
| `E2E_FRONTEND_URL` | `LIVE_FRONTEND_URL` |

JWT is obtained at runtime via `POST ${LIVE_API_URL}/auth/login` — do not store long-lived tokens in `.env`.

### Redeploy order

1. Deploy **metar-api** with updated `METAR_CORS_ORIGINS`.
2. Rebuild **metar-frontend** with `VITE_API_BASE_URL` pointing to live API.
3. Run H4 CORS preflight + H5 bundle verification.

See `.cursor/skills/connectivity-gates.md` for H-tier definitions.

## Local Development

```bash
cp .env.example .env
make install
make dev
# Or: docker compose up --build
```

Post-migration compose: **backend + frontend** (two services).

## Docker Build Context

| Image | Context | Dockerfile |
|-------|---------|------------|
| API | repo root | `apps/backend/docker/Dockerfile` |
| Frontend | `apps/frontend` | `apps/frontend/Dockerfile` |

API image must include: apps/backend, packages/auth, packages/gifts, packages/shared, vendor/schemas.

## Health Checks

```
GET /health
```

Render health check path: `/health` on metar-api.

## Migrations

No database migrations in monorepo v1 (Supabase external). Document future Postgres if added.

## Rollback

Redeploy previous Render deploy from dashboard or revert git tag on main.

## Checklist (pre-deploy)

- [ ] CI green on main
- [ ] E2E T2 pass locally
- [ ] Env vars set on Render
- [ ] CORS origins include production frontend URL
- [ ] Frontend rebuilt after API URL known

## Runbook

### Live test harness (T3 — manual signoff)

Run from repo root after populating `.env` with live URLs and admin credentials.
**Prerequisite**: E2E-001 schema path fix merged (blocks H3 validate + full H6 UJ-002).

```bash
# Individual tiers
make test-live-connectivity   # H4–H5
make test-live-api            # H3 pytest (-m live_api)
make test-live-e2e            # H6 Playwright UJ-001–003

# Full sequential signoff (recommended before release)
make test-live                # H4–H5 → H3 → H6
```

**Cold-start**: Live tests retry up to 3 times with 30s backoff when Render services are spun down.

**Rate limits**: Live API tests use exponential backoff on HTTP 429.

### Connectivity tiers (H3–H6)

| Tier | What | Command | Required env |
|------|------|---------|--------------|
| H3 | Live API smoke | `make test-live-api` | `LIVE_API_URL`, `ADMIN_*` |
| H0c | CORS policy (in-process) | `pytest apps/backend/tests/unit/test_cors_policy.py` | — |
| H0i | API integration | `pytest apps/backend/tests/integration` | local stack |
| H4 | Live CORS preflight | `make test-live-connectivity` | `LIVE_API_URL`, `LIVE_FRONTEND_URL` |
| H5 | Frontend bundle URLs | `make test-live-connectivity` | `LIVE_FRONTEND_URL`, `VITE_API_BASE_URL` |
| H6 | Live Playwright | `make test-live-e2e` | `PLAYWRIGHT_BASE_URL`, `ADMIN_*` |

### Post-deploy sequence

1. Confirm API health: `curl -sf "${LIVE_API_URL}/health"`
2. Run connectivity + live signoff:

   ```bash
   export LIVE_API_URL="https://metar-to-iwxxm-api.onrender.com"
   export LIVE_FRONTEND_URL="https://metar-to-iwxxm-frontend-v4-web.onrender.com"
   export PLAYWRIGHT_BASE_URL="${LIVE_FRONTEND_URL}"
   export VITE_API_BASE_URL="${LIVE_API_URL}"
   # ADMIN_EMAIL / ADMIN_PASSWORD from .env
   make test-live
   ```

3. If H5 fails, rebuild **metar-frontend** with correct `VITE_API_BASE_URL` and redeploy.

### Env vars (connectivity)

| Variable | Service | Purpose |
|----------|---------|---------|
| `METAR_CORS_ORIGINS` | metar-api | Allowed browser origins (comma-separated) |
| `VITE_API_BASE_URL` | metar-frontend (build) | API base URL embedded in static bundle |
| `LIVE_API_URL` | live test scripts | Live API base for H3–H4 |
| `LIVE_FRONTEND_URL` | live test scripts | Browser origin for H4 + Playwright base for H6 |
| `PLAYWRIGHT_BASE_URL` | Playwright (H6) | Same as `LIVE_FRONTEND_URL` for remote runs |

See [staging-secrets-matrix.md](staging-secrets-matrix.md) for staging values.

## References

- `render.yaml` — Render Blueprint (API + static frontend)
- [staging-secrets-matrix.md](staging-secrets-matrix.md) — staging env values
- [user-journeys.md](user-journeys.md) UJ-OPS-001
- Legacy three-service docs: [ARCHIVE/pre-monorepo-deploy/](ARCHIVE/pre-monorepo-deploy/)
