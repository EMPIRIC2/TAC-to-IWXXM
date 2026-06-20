# Deployment

> **Project**: METAR to IWXXM Converter
> **Platform**: Render (Docker web service + static site)
> **Last updated**: 2026-06-14

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

### Connectivity tiers (H4–H5)

| Tier | What | Command | Required env |
|------|------|---------|--------------|
| H0c | CORS policy (in-process) | `pytest tests/unit/test_cors_policy.py` | — |
| H0i | API integration | `pytest apps/backend/tests/integration` (post-migration) | local stack |
| H4 | Live CORS preflight | `pytest tests/smoke/test_staging_connectivity.py -m live` | `STAGING_API_URL`, `STAGING_FRONTEND_ORIGIN` |
| H5 | Frontend bundle URLs | `bash scripts/deploy/verify_connectivity.sh` | `STAGING_FRONTEND_URL`, `VITE_API_BASE_URL` |

### Post-deploy sequence

1. Confirm API health: `curl -sf "${STAGING_API_URL}/health"`
2. Run full connectivity script:

   ```bash
   export STAGING_API_URL="https://metar-api.example.onrender.com"
   export STAGING_FRONTEND_ORIGIN="https://metar-frontend.example.onrender.com"
   export STAGING_FRONTEND_URL="https://metar-frontend.example.onrender.com"
   export VITE_API_BASE_URL="https://metar-api.example.onrender.com"
   bash scripts/deploy/verify_connectivity.sh
   ```

3. If H5 fails, rebuild **metar-frontend** with correct `VITE_API_BASE_URL` and redeploy.

### Env vars (connectivity)

| Variable | Service | Purpose |
|----------|---------|---------|
| `METAR_CORS_ORIGINS` | metar-api | Allowed browser origins (comma-separated) |
| `VITE_API_BASE_URL` | metar-frontend (build) | API base URL embedded in static bundle |
| `STAGING_API_URL` | smoke scripts | Live API base for H4 |
| `STAGING_FRONTEND_ORIGIN` | smoke scripts | Browser Origin header for CORS preflight |
| `STAGING_FRONTEND_URL` | smoke scripts | CDN URL for H5 bundle inspection |

See [staging-secrets-matrix.md](staging-secrets-matrix.md) for staging values.

## References

- `render.yaml` — Render Blueprint (API + static frontend)
- [staging-secrets-matrix.md](staging-secrets-matrix.md) — staging env values
- [user-journeys.md](user-journeys.md) UJ-OPS-001
- Legacy three-service docs: [ARCHIVE/pre-monorepo-deploy/](ARCHIVE/pre-monorepo-deploy/)
