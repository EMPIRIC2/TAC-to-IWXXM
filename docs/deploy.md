# Deployment

> **Project**: METAR to IWXXM Converter
> **Platform**: Render (Docker web service + static site)
> **Last updated**: 2026-06-23 (S003 env/config delta)

## Topology (post-monorepo)

| Service | Type | Source | Port |
|---------|------|--------|------|
| metar-api | Web (Docker) | `apps/backend` Dockerfile | `$PORT` (0.0.0.0) |
| metar-frontend | **Static site** (CDN) | `apps/frontend` Vite build | CDN |

Auth is **not** a separate deployable — included in metar-api via packages/auth.

**Observability**: Render built-in logs only — Loki/Prometheus/Grafana removed from Blueprint (ADR-006).

## Integration

> **S003 delta:** Secrets-only `.env`; non-secrets in `config/{local,prod}.json`. See
> [config-spec.md](config-spec.md), [env-contract.md](env-contract.md), ADR-010.

### Secrets (API runtime — Render dashboard, `sync: false`)

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_PUBLISHABLE_KEY` | Yes | `sb_publishable_*` — JWT validation |
| `SUPABASE_SECRET_KEY` | Yes | `sb_secret_*` — Auth Admin API scripts only |
| `DATABASE_URL` | Yes | Postgres pooler from Supabase Connect |
| `METAR_CONFIG_ENV` | Yes (prod) | `prod` on Render; selects `config/prod.json` |

### Non-secrets (`config/prod.json` — committed)

| Field | Description |
|-------|-------------|
| `api.baseUrl` | HTTPS URL of metar-api (`/api/v1`, `/auth`, `/admin`) |
| `api.frontendUrl` | Public static site URL (auth redirects) |
| `api.corsOrigins` | Allowed browser origins |
| `api.disableAuth` | `false` in production |
| `supabase.url` | Supabase project URL |
| `validation.*`, `observability.*` | WMO validation and logging flags |
| `liveE2e.*` | Canonical URLs for `make test-live*` |

### Frontend static deploy

1. Copy `config/prod.json` → `public/config.json` at build.
2. Inject `supabase.publishableKey` from `SUPABASE_PUBLISHABLE_KEY` (dashboard secret — not in git).
3. App fetches `/config.json` at bootstrap (replaces `VITE_*` build-time embed per ADR-010).

### Local development

| Setting | Source |
|---------|--------|
| Secrets | Repo-root `.env` (five vars — see `.env.example`) |
| URLs / CORS / flags | `config/local.json` via `METAR_CONFIG_ENV=local` |
| Ports | Frontend **18000**, API **18001** (standardized S003-R4) |

### Live test (manual T3 — credentials in `.env` only)

| Variable | Source |
|----------|--------|
| `LIVE_API_URL` | `config/prod.json` → `liveE2e.apiUrl` (override via env optional) |
| `LIVE_FRONTEND_URL` | `config/prod.json` → `liveE2e.frontendUrl` |
| `PLAYWRIGHT_BASE_URL` | Same as `LIVE_FRONTEND_URL` for H6 |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Local `.env` only |

JWT via `POST ${LIVE_API_URL}/auth/login` — no long-lived tokens in `.env`.

**Deprecated** (one-release shim): `VITE_*`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`,
`METAR_CORS_ORIGINS`, `FRONTEND_URL`, `DISABLE_AUTH`, `STAGING_*`, `E2E_*`.

Operator sync: [env-sync-runbook.md](env-sync-runbook.md). Verify: `make env-check`.

### Redeploy order

1. Deploy **metar-api** with secrets + `METAR_CONFIG_ENV=prod` (CORS from `config/prod.json`).
2. Rebuild **metar-frontend** with `/config.json` injection.
3. Run H4 CORS preflight + H5 bundle verification + `make env-check`.

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
| Frontend | repo root | `apps/frontend/Dockerfile` |

API image must include: apps/backend, packages/auth, packages/gifts, packages/shared, vendor/schemas.

Frontend image must include: apps/frontend, packages/shared (pnpm workspace dep `@metar/shared`).

## Health Checks

```
GET /health
```

Render health check path: `/health` on metar-api.

## Migrations

Supabase migrations live in `supabase/migrations/` and are applied externally (not at API boot).

### F5 work sessions (EV-004)

Before deploying F5 to production:

1. **S003 gate** — rotate to `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY`; run `make env-check`.
2. **Advisor migrations** — apply `003`–`006` (security advisors) on the METAR Supabase project.
3. **F5 schema** — apply `20250623000007_metar_work_sessions.sql` (table, RLS, WIP index, pg_cron retention per ADR-012).
4. **Verify locally** — `make supabase-reset` then `pytest tests/integration/test_metar_work_sessions_migration.py` and `apps/backend/tests/integration/test_work_session_tc004.py`.
5. **Redeploy API** — work-sessions routes require a new API deploy; no new Render secrets.

Operator reference: [env-sync-runbook.md](env-sync-runbook.md), ADR-011, ADR-012.

## Rollback

Redeploy previous Render deploy from dashboard or revert git tag on main.

## Checklist (pre-deploy)

- [ ] CI green on main
- [ ] E2E T2 pass locally
- [ ] Env vars set on Render
- [ ] CORS origins include production frontend URL
- [ ] Frontend rebuilt after API URL known
- [ ] F5: Supabase migrations through `20250623000007` applied (staging/prod)
- [ ] F5: S003 key rotation complete (`make env-check` no legacy key WARN)

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
