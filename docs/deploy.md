# Deployment

> **Project**: METAR to IWXXM Converter
> **Platform**: Render (Docker web service + static site + Background Worker)
> **Last updated**: 2026-07-21 (S019 / EV-014 T2.7 — SQL Server ODBC driver notes)

## Topology (post-monorepo + F8)

| Service | Type | Source | Port |
|---------|------|--------|------|
| metar-api | Web (Docker) | `apps/backend` Dockerfile | `$PORT` (0.0.0.0) |
| metar-frontend | **Static site** (CDN) | `apps/frontend` Vite build | CDN |
| metar-worker | **Background Worker** | `apps/worker` (ADR-018) | N/A (no HTTP) |

**Staging worker (T7.1)**: `metar-to-iwxxm-worker` —
`srv-d99u0i8k1i2s73eq5oqg` (docker-from-git, branch `feat/S008-M6-worker` until cutover
merges to `main`). Dashboard:
https://dashboard.render.com/worker/srv-d99u0i8k1i2s73eq5oqg

Auth is **not** a separate deployable — included in metar-api via packages/auth.
F8 worker shares packages with the API image family but is a **separate** Render service.

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

### Secrets (Worker runtime — F8, ADR-018)

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service-role JWT for store/quarantine writers |
| `INGEST_POLLER_URL` | Yes | HTTPS / object-prefix fixture or feed URL |
| `INGEST_POLL_INTERVAL_SEC` | Yes | Poll interval (seconds) |

### Non-secrets (`config/prod.json` — committed)

| Field | Description |
|-------|-------------|
| `api.baseUrl` | HTTPS URL of metar-api (`/api/v1`, `/auth`) — **no** `/admin` |
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
| `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | Local `.env` / CI — ordinary user for live login (replaces `ADMIN_*`) |

JWT via `POST ${LIVE_API_URL}/auth/login` — no long-lived tokens in `.env`.

**Deprecated** (one-release shim): `VITE_*`, `SUPABASE_ANON_KEY` (frontend),
`METAR_CORS_ORIGINS`, `FRONTEND_URL`, `ADMIN_EMAIL` / `ADMIN_PASSWORD`.
(`SUPABASE_SERVICE_ROLE_KEY` remains canonical for **F8 worker** writers per env-contract.)

Operator sync: [env-sync-runbook.md](ops/env-sync-runbook.md). Verify: `make env-check`.

### Redeploy order

1. Deploy **metar-api** with secrets + `METAR_CONFIG_ENV=prod` (CORS from `config/prod.json`).
2. Rebuild **metar-frontend** with `/config.json` injection.
3. Deploy **metar-worker** with poller + service-role secrets (after F8 migrations applied).
4. Run H4 CORS preflight + H5 bundle verification + H6/H7 as applicable + `make env-check`.

See `.cursor/skills/connectivity-gates.md` for H-tier definitions.

## Local Development

```bash
cp .env.example .env
make install
make dev
# Or: docker compose up --build
```

Post-migration compose: **backend + frontend** (two services). Worker may run via
`make worker` / separate process locally (T6.2).

### SQL Server ODBC (F16 / E14-06)

BYOC SQL Server sinks use SQLAlchemy async + **aioodbc** (`mssql+aioodbc://`). A **system
ODBC SQL Server driver** must be registered with the host ODBC manager — Python wheels alone
are not enough. Preferred driver: **Microsoft ODBC Driver 18 for SQL Server** (then 17);
**FreeTDS** is accepted as a fallback. Probe helpers live in
`packages/dissemination` (`dissemination.odbc`).

**Verify install**

```bash
uv run python -c "from dissemination.odbc import list_sqlserver_odbc_drivers, odbc_sqlserver_available; print(list_sqlserver_odbc_drivers()); print(odbc_sqlserver_available())"
```

**Debian / Ubuntu (Microsoft Driver 18)** — follow current Microsoft docs for the distro
codename; typical shape:

```bash
# unixODBC + Microsoft package repo, then:
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```

**macOS**: install via Microsoft’s Homebrew tap (`msodbcsql18`) or their pkg installer.

**URI shape** (driver query param required at connect time; integration tests attach the
preferred driver automatically):

```text
mssql+aioodbc://USER:PASS@HOST:1433/DB?driver=ODBC+Driver+18+for+SQL+Server
# Testcontainers / self-signed TLS often also need:
#   &TrustServerCertificate=yes
```

**CI / tests**: `make test-integration-dissemination` runs SQL Server cases only when Docker
**and** an ODBC SQL Server driver are present; otherwise those cases **skip** (TC-F16-003 /
E14-06). Default CI images may omit ODBC — that is expected.

**API Docker image**: `apps/backend/docker/Dockerfile` does **not** currently install
`msodbcsql18`. Stock Render **metar-api** cannot open SQL Server BYOC URIs until the image
(or base) gains a system ODBC SQL Server driver. Postgres / MySQL / SQLite sinks do not need
ODBC. Package README: [`packages/dissemination/README.md`](../packages/dissemination/README.md).

## Docker Build Context

| Image | Context | Dockerfile |
|-------|---------|------------|
| API | repo root | `apps/backend/docker/Dockerfile` |
| Frontend | repo root | `apps/frontend/Dockerfile` |
| Worker | repo root | `apps/worker/Dockerfile` (T6.2) |

API image must include: apps/backend, packages/auth, packages/tac2iwxxm (post-cutover; gifts
until then), packages/tac-validate, packages/iwxxm-validate, packages/shared, vendor/schemas.

Worker image must include: apps/worker, same packages as API (no frontend).

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

Operator reference: [env-sync-runbook.md](ops/env-sync-runbook.md), ADR-011, ADR-012.

### Supabase CI sync

`.github/workflows/supabase-sync.yml` applies schema changes and deploys legacy edge
functions to project `ktvxijislbtgqapllmuk` on every push to `main` (and via manual
dispatch). Pull requests against `main` run a read-only migration dry-run only.

| Job | What | Source path |
|-----|------|-------------|
| `migrations` | `supabase db push --linked` | `supabase/migrations/` |
| `functions` | `supabase functions deploy` | `apps/frontend/supabase/functions/` |

**GitHub configuration** (Settings → Secrets and variables → Actions):

| Kind | Name | Purpose |
|------|------|---------|
| Secret | `SUPABASE_ACCESS_TOKEN` | `sbp_…` CI token for Supabase CLI |
| Secret | `SUPABASE_DB_PASSWORD` | Database password for `link` + `db push` |
| Variable | `SUPABASE_PROJECT_REF` | Optional; defaults to `ktvxijislbtgqapllmuk` |

The `functions` job copies root `supabase/config.toml` into `apps/frontend/supabase/` at
CI time (that tree has functions but no config). Auth routes run on metar-api; edge
functions remain only for the database-upload path until a follow-up retires them
(ADR-010).

Manual equivalent: `make supabase-push` (migrations) or `bash scripts/supabase/db-push.sh`.

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
- [ ] GitHub: `SUPABASE_ACCESS_TOKEN` and `SUPABASE_DB_PASSWORD` set for supabase-sync workflow

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
| H3 | Live API smoke | `make test-live-api` | `LIVE_API_URL`, `E2E_USER_*` (when auth on) |
| H0c | CORS policy (in-process) | `pytest apps/backend/tests/unit/test_cors_policy.py` | — |
| H0i | API integration | `pytest apps/backend/tests/integration` | local stack |
| H4 | Live CORS preflight | `make test-live-connectivity` | `LIVE_API_URL`, `LIVE_FRONTEND_URL` |
| H5 | Frontend bundle URLs | `make test-live-connectivity` | `LIVE_FRONTEND_URL`, `VITE_API_BASE_URL` |
| H6 | Live Playwright | `make test-live-e2e` | `PLAYWRIGHT_BASE_URL`, `E2E_USER_*` |

### Post-deploy sequence

1. Confirm API health: `curl -sf "${LIVE_API_URL}/health"`
2. Run connectivity + live signoff:

   ```bash
   export LIVE_API_URL="https://metar-to-iwxxm-api.onrender.com"
   export LIVE_FRONTEND_URL="https://metar-to-iwxxm-frontend-v4-web.onrender.com"
   export PLAYWRIGHT_BASE_URL="${LIVE_FRONTEND_URL}"
   export VITE_API_BASE_URL="${LIVE_API_URL}"
   # E2E_USER_EMAIL / E2E_USER_PASSWORD from .env (when auth enabled)
   make test-live
   ```

3. If H5 fails, rebuild **metar-frontend** with correct `VITE_API_BASE_URL` and redeploy.

### Env vars (connectivity)

| Variable | Service | Purpose |
|----------|---------|---------|
| `METAR_CORS_ORIGINS` | metar-api | Allowed browser origins (comma-separated) |
| `DISSEMINATION_EGRESS_ALLOWLIST` | metar-api | Host/CIDR allowlist for BYOC dissemination egress (ADR-029); empty = fail-closed |
| `VITE_API_BASE_URL` | metar-frontend (build) | API base URL embedded in static bundle |
| `LIVE_API_URL` | live test scripts | Live API base for H3–H4 |
| `LIVE_FRONTEND_URL` | live test scripts | Browser origin for H4 + Playwright base for H6 |
| `PLAYWRIGHT_BASE_URL` | Playwright (H6) | Same as `LIVE_FRONTEND_URL` for remote runs |

See [staging-secrets-matrix.md](ops/staging-secrets-matrix.md) for staging values.

## PyPI package publish (S014 / EV-010 / F12–F14)

Library packages publish **independently** of Render via GitHub Actions **OIDC trusted
publishing** on version tags:

| Package | Tag pattern | PyPI name |
|---------|-------------|-----------|
| `packages/tac-validate` | `tac-validate-v*` | `tac-validate` |
| `packages/iwxxm-validate` | `iwxxm-validate-v*` | `iwxxm-validate` |
| `packages/tac2iwxxm` | `tac2iwxxm-v*` | `tac2iwxxm` |

**First release**: `0.1.0` for each. **One** GitHub Actions workflow with a **package matrix**
(three packages) builds sdist+wheel (maturin manylinux/macOS/win for native crates), optional
smoke-install, then publishes on matching version tags. Configure PyPI Trusted Publisher +
workflow `id-token: write` (see config-spec §F11–F14). Prefer no long-lived `PYPI_API_TOKEN`
when OIDC is available.

**Render this cycle**: Still required (E10-15) because msgspec **response** shapes may change —
redeploy API then frontend; run H4–H5 + UJ-022. PyPI publish does not replace Render smokes.

## References

- `render.yaml` — Render Blueprint (API + static frontend)
- [staging-secrets-matrix.md](ops/staging-secrets-matrix.md) — staging env values
- [user-journeys.md](user-journeys.md) UJ-OPS-001, UJ-023
- [config-spec.md](config-spec.md) §F11–F14
- [ADR-026](adr/ADR-026-msgspec-http-openapi.md)
- Legacy three-service docs: [ARCHIVE/pre-monorepo-deploy/](ARCHIVE/pre-monorepo-deploy/)
