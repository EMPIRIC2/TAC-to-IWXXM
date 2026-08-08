# Deployment

> **Project**: METAR to IWXXM Converter
> **Platform**: **DOKS** (F30 primary) · Render **suspended** (T6.5 / `D-S038-t65-waive`)
> **Last updated**: 2026-08-08 (S053 / EV-044 — dual DOKS clusters + DO Projects)

## Topology (F30 — DOKS dual env / dual cluster)

| Workload | Type | Source | Notes |
|----------|------|--------|-------|
| metar-api | Deployment / Service | `apps/backend` image | `$PORT` on `0.0.0.0`; `/api/v1/*` + `/auth/*` |
| metar-frontend | Static / CDN or nginx | `apps/frontend` Vite build | `/config.json` inject |
| metar-worker | Deployment (Background) | `apps/worker` image | No public HTTP; `DATABASE_URL` |

| `env_role` | Branch | DO Project | Cluster | Namespace | Hosts |
|------------|--------|------------|---------|-----------|-------|
| staging | `stage` | **Staging TAC-to-IWXXM** | `metar-iwxxm-staging` | `metar-iwxxm-staging` | `https://api.staging.tac-to-iwxxm.com`, `https://app.staging.tac-to-iwxxm.com` |
| prod | `main` | **TAC-to-IWXXM** | `metar-iwxxm` | `metar-iwxxm` | `https://api.tac-to-iwxxm.com`, `https://app.tac-to-iwxxm.com` |

**IaC (T6.1 / #712 / EV-043 / EV-044):** Kustomize overlays at
[`deploy/doks/overlays/{staging,prod}`](../deploy/doks/) —
`kubectl apply -k deploy/doks/overlays/staging` (or `prod`) against the **matching** cluster.
Secrets create out-of-band.
Staging DNS: [ops/doks-staging-dns-runbook.md](ops/doks-staging-dns-runbook.md). Promote path:
[ADR-034](adr/ADR-034-doks-staging-promote-from-stage.md).

**Release migrate (T6.2):** API Deployment **initContainer** runs idempotent
`alembic upgrade head` (same as `make db-migrate` / CI). Optional Job:
`deploy/doks/base/job-alembic-upgrade.yaml`.

**Product DB**: DigitalOcean Postgres (`DATABASE_URL`) — sessions + F8 store/quarantine.  
**Auth**: Supabase Auth only (**JWKS**). No Supabase product DB on default path (ADR-033).

### DOKS public hostnames (T6.3 + EV-043 / EV-044 staging)

| Role | Prod | Staging |
|------|------|---------|
| API | `https://api.tac-to-iwxxm.com` | `https://api.staging.tac-to-iwxxm.com` |
| Frontend | `https://app.tac-to-iwxxm.com` | `https://app.staging.tac-to-iwxxm.com` |
| Worker | (in-cluster) | (in-cluster) |
| DO Project | TAC-to-IWXXM | Staging TAC-to-IWXXM |
| Cluster | `metar-iwxxm` | `metar-iwxxm-staging` |
| LB | `168.144.12.70` (prod) | **staging LB** (new EXTERNAL-IP after EV-044 provision) |
| Config profile | `config/prod.json` | `config/staging.json` |
| Product DB | DO Postgres `metar-iwxxm` / `defaultdb` | DO Postgres `metar-iwxxm-staging` (dedicated) |

Soak checklist (closed early under `D-S038-t65-waive`):
[ops/doks-cutover-soak-checklist.md](ops/doks-cutover-soak-checklist.md).
Render archive: [ops/render-decommission-archive.md](ops/render-decommission-archive.md).

### Render (historical — TC-F30-005 / T6.5)

| Service | Service ID | Status |
|---------|------------|--------|
| `metar-to-iwxxm-api` | `srv-d69v688gjchc73cn9kg0` | **suspended** 2026-08-03 |
| `metar-to-iwxxm-frontend-v4-web` | `srv-d6cvj2i4d50c73aelapg` | **suspended** 2026-08-03 |
| `metar-to-iwxxm-worker` | `srv-d99u0i8k1i2s73eq5oqg` | **suspended** 2026-08-03 |

**CI hotfix (2026-08-03):** `scripts/deploy/trigger_render_image_deploy.py` supports
`--skip-if-suspended` / `RENDER_SKIP_IF_SUSPENDED` so main CI Deploy skips suspended Render
services without failing (see BUG-2026-08-03). GHCR push continues; DOKS is the prod target.

### CD — DOKS image rollout (S042 / EV-034 / EV-043 / EV-044 dual cluster)

| Branch | GH Environment | Cluster | Namespace | Latest tag | Post-deploy |
|--------|----------------|---------|-----------|------------|-------------|
| `stage` | `staging` | `metar-iwxxm-staging` | `metar-iwxxm-staging` | `stage-latest` | **Staging smoke** job |
| `main` | `production` | `metar-iwxxm` | `metar-iwxxm` | `main-latest` | (prod smoke via 13 / Makefile) |

On push to `stage` or `main`, **Deploy** in `.github/workflows/ci-cd.yml`:

1. Builds/pushes GHCR images tagged `TIMESTAMP-SHA` and `{stage\|main}-latest`.
2. **Rolls DOKS** with `DOKS_NAMESPACE` + **env-scoped kubeconfig** via
   `scripts/deploy/doks_rollout_images.sh <tag>` (staging secret ≠ prod secret after EV-044).
3. **Render hooks** (optional, **main only**): `--skip-if-suspended` (`E34-4`).

**Promote:** Feature → PR → `stage` → Staging smoke → PR **`stage`→`main`** (job
**Staging gate** / `scripts/ci/staging_gate.sh`) → prod Deploy. Solo-dev: PR is the
manual gate (no Environment reviewers). See [ADR-034](adr/ADR-034-doks-staging-promote-from-stage.md).

| Actions secret | Required | Description |
|----------------|----------|-------------|
| `KUBE_CONFIG` (production env) | **Yes** (prod Deploy) | Base64 kubeconfig for **prod** cluster `metar-iwxxm` / ns `metar-iwxxm`. Static SA/token — not `doctl` exec. |
| `KUBE_CONFIG` (staging env) or `KUBE_CONFIG_STAGING` | **Yes** (staging Deploy) | Base64 kubeconfig for **staging** cluster `metar-iwxxm-staging` / ns `metar-iwxxm-staging`. |

Encode: `base64 -w0 <kubeconfig.yaml>` (macOS: `base64 -i kubeconfig.yaml | tr -d '\n'`).

Branch protection / Environments (admin): `bash scripts/deploy/apply_gh_branch_rulesets.sh`
+ [ops/doks-staging-dns-runbook.md](ops/doks-staging-dns-runbook.md).

**F21 Amended / F31**: Optional Auth restored via `packages/auth`. Convert remains public.
F8 worker runs on DOKS.

**Observability**: Platform logs (DOKS). Loki/Prometheus/Grafana remain out of Blueprint
(ADR-006) unless a later evolve adds them.

## Integration

> **S003 delta:** Secrets-only `.env`; non-secrets in `config/{local,prod}.json`. See
> [config-spec.md](config-spec.md), [env-contract.md](env-contract.md), ADR-010.
> **F30/F31**: Canonical env contract — Auth-only Supabase + DO Postgres + DOKS —
> [env-contract.md](env-contract.md). Data migrate:
> [ops/supabase-to-do-postgres-migration.md](ops/supabase-to-do-postgres-migration.md).

### Secrets (API runtime — DOKS)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | DigitalOcean Postgres — sessions + shared product DB |
| `SUPABASE_URL` | Yes (Auth) | Supabase Auth project URL |
| `SUPABASE_JWKS_URL` | No (default from `SUPABASE_URL`) | JWKS-only server verify — never FE; **not** `SUPABASE_JWT_SECRET` |
| `RATE_LIMIT_PUBLIC_PER_MIN` | No (default 60) | Public convert/validate rate limit |
| `RATE_LIMIT_DISSEMINATION_PER_MIN` | No (default 10) | Dissemination preflight/send rate limit |
| `MAX_REQUEST_BODY_BYTES` | No (default 2 MiB) | Request body cap |
| `DISSEMINATION_EGRESS_ALLOWLIST` | Yes for F16–F19 | Host/CIDR allowlist (empty ⇒ deny) |
| `METAR_CONFIG_ENV` | Yes (prod) | `prod`; selects `config/prod.json` |

**Static inject:** `SUPABASE_PUBLISHABLE_KEY` into `/config.json` for optional login.
**Do not** use `SUPABASE_SERVICE_ROLE_KEY` as product DB writer after F30.

### Secrets (Worker runtime — F8, ADR-018 amended)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | DO Postgres store/quarantine |
| `INGEST_POLLER_URL` | Yes | HTTPS JSON feed (or object-prefix listing). **Must** be `https://` — never `REPLACE_ME_*` |
| `INGEST_POLL_INTERVAL_SEC` | Yes | Poll interval (seconds) |

**Non-prod fixture URL (EV-033 — pin this when no operational feed):**

```
https://raw.githubusercontent.com/EMPIRIC2/TAC-to-IWXXM/main/apps/worker/tests/fixtures/ingest_feed.json
```

**DOKS fail-closed (EV-033):** keep `metar-worker` at **0 replicas** until
`bash scripts/deploy/doks_worker_poller_preflight.sh --probe` passes, then
`--scale-up`. Do **not** copy `INGEST_POLLER_URL` from suspended Render worker env
without probing (legacy fork/branch raw URLs often 404). CrashLoop check:
`bash scripts/deploy/check_worker_crashloop.sh`. Details:
[deploy/doks/README-worker-hardening.md](../deploy/doks/README-worker-hardening.md).

### Non-secrets (`config/prod.json` — committed)

| Field | Description |
|-------|-------------|
| `api.baseUrl` | HTTPS URL of metar-api (`/api/v1` **and** `/auth` — **no** `/admin`) |
| `api.frontendUrl` | Public static site URL |
| `api.corsOrigins` | Allowed browser origins (DOKS FE after cutover) |
| `supabase.url` | Auth project URL (public) |
| `validation.*`, `observability.*` | WMO validation and logging flags |
| `liveE2e.*` | Canonical URLs for `make test-live*` (DOKS after cutover) |

### Frontend static deploy

1. Copy `config/prod.json` → `public/config.json` at build.
2. Inject `SUPABASE_PUBLISHABLE_KEY` for Auth bootstrap.
3. App fetches `/config.json` at bootstrap (ADR-010).
4. Guest history remains IndexedDB; logged-in uses work-sessions APIs; F22 prefs localStorage.

### Local development

| Setting | Source |
|---------|--------|
| Secrets | Repo-root `.env` (see `.env.example` + env-contract) |
| URLs / CORS / flags | `config/local.json` via `METAR_CONFIG_ENV=local` |
| Ports | Frontend **18000**, API **18001** (standardized S003-R4) |

### Live test (manual T3 — F30/F31)

| Variable | Source |
|----------|--------|
| `LIVE_API_URL` | `config/prod.json` → `liveE2e.apiUrl` (DOKS after cutover) |
| `LIVE_FRONTEND_URL` | `config/prod.json` → `liveE2e.frontendUrl` |
| `PLAYWRIGHT_BASE_URL` | Same as `LIVE_FRONTEND_URL` for H6 |
| `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` | Optional — UJ-046 / session CRUD only |

Convert remains public (no JWT). **H4–H5 required** this cycle (`D-S038-tp`).

Operator sync: [env-sync-runbook.md](ops/env-sync-runbook.md). Verify: `make env-check`.

### Redeploy order / cutover

1. Apply Alembic to DO Postgres; one-time migrate legacy Supabase product rows.
2. Deploy **metar-api** with `DATABASE_URL` + Auth verify + CORS for DOKS FE.
3. Rebuild **metar-frontend** with `/config.json` + publishable Auth key.
4. Deploy **metar-worker** with `DATABASE_URL` + poller env.
5. Run **H0–H5** (H4–H5 required) + H6 public + Auth session smoke + F8 store smoke.
6. Soak + Render decommission (TC-F30-005) — **done** under `D-S038-t65-waive` (see archive).

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

### wis2box Compose harness (F17 / E14-04)

Staging WIS2 uses a **Docker Compose / CI harness** — not a Render web service. Image build
context: `packages/dissemination/docker/wis2box-harness` (MQTT `:1883` + HTTP dataset
`:8080` / host `:9080`). Overlay: `docker-compose.wis2box.yml` (profile `wis2box`).

```bash
make compose-wis2box-up
curl -s http://127.0.0.1:9080/health
make compose-wis2box-harness   # CI hook: up + probe + PUT/GET smoke
make compose-wis2box-down
```

**Local / CI harness (recommended):**

```bash
DISSEMINATION_EGRESS_ALLOWLIST=wis2box,127.0.0.1,127.0.0.0/8,localhost
```

(`scripts/ci/run_wis2box_harness.sh` defaults to the same list when unset.)

**Render / prod:** leave empty (fail-closed) when not demoing. For live BYOC close-gate
demos (TC-F17-002 / TC-F18-002), set only the exact operator Postgres / WIS2 / EDIS SMTP
hostnames — never wildcards or destination secrets. Live WIS2 acceptance remains operator
BYOC.

## Docker Build Context

| Image | Context | Dockerfile |
|-------|---------|------------|
| API | repo root | `apps/backend/docker/Dockerfile` |
| Frontend | repo root | `apps/frontend/Dockerfile` |
| Worker | repo root | `apps/worker/Dockerfile` (T6.2) |

API image must include: apps/backend, packages/tac2iwxxm, packages/tac-validate,
packages/iwxxm-validate, packages/dissemination, packages/shared, vendor/schemas.
(**No** `packages/auth` — deleted F21 / EV-017.)

Worker image must include: apps/worker, same packages as API (no frontend).

Frontend image must include: apps/frontend, packages/shared (pnpm workspace dep `@metar/shared`).

## Health Checks

```
GET /health
```

Render health check path: `/health` on metar-api.

## Migrations

Supabase migrations live in `supabase/migrations/` and are applied externally (not at API boot).

### F5 work sessions (EV-004) — **historical; superseded by F21 IndexedDB**

Server `tac_work_sessions` + Auth/RLS path is **retired** for the operator product (F21 /
ADR-031). Work history is browser IndexedDB. Legacy rows may be archived ~30 days (ops note
from T5.5) — not a product API.

Historical apply steps (archive only):

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
| H3 | Live API smoke | `make test-live-api` | `LIVE_API_URL` (public — no Auth) |
| H0c | CORS policy (in-process) | `pytest apps/backend/tests/unit/test_cors_policy.py` | — |
| H0i | API integration | `pytest apps/backend/tests/integration` | local stack |
| H4 | Live CORS preflight | `make test-live-connectivity` | `LIVE_API_URL`, `LIVE_FRONTEND_URL` |
| H5 | Frontend bundle URLs | `make test-live-connectivity` | `LIVE_FRONTEND_URL`, `VITE_API_BASE_URL` |
| H6 | Live Playwright | `make test-live-e2e` | `PLAYWRIGHT_BASE_URL` (public; `TC-F21-auth-gone`) |

### Post-deploy sequence

1. Confirm API health: `curl -sf "${LIVE_API_URL}/health"`
2. Run connectivity + live signoff:

   ```bash
   export LIVE_API_URL="https://metar-to-iwxxm-api.onrender.com"
   export LIVE_FRONTEND_URL="https://metar-to-iwxxm-frontend-v4-web.onrender.com"
   export PLAYWRIGHT_BASE_URL="${LIVE_FRONTEND_URL}"
   export VITE_API_BASE_URL="${LIVE_API_URL}"
   # F21: no E2E_USER_* — public convert
   make test-live
   ```

3. If H5 fails, rebuild **metar-frontend** with correct `VITE_API_BASE_URL` and redeploy.

### Env vars (connectivity)

| Variable | Service | Purpose |
|----------|---------|---------|
| `METAR_CORS_ORIGINS` | metar-api | Allowed browser origins (comma-separated) |
| `DISSEMINATION_EGRESS_ALLOWLIST` | metar-api | Host/CIDR allowlist for BYOC dissemination egress (ADR-029); empty = fail-closed; local/CI use `wis2box,127.0.0.1,127.0.0.0/8,localhost`; live demos = exact BYOC hosts only |
| `VITE_API_BASE_URL` | metar-frontend (build) | API base URL embedded in static bundle |
| `LIVE_API_URL` | live test scripts | Live API base for H3–H4 |
| `LIVE_FRONTEND_URL` | live test scripts | Browser origin for H4 + Playwright base for H6 |
| `PLAYWRIGHT_BASE_URL` | Playwright (H6) | Same as `LIVE_FRONTEND_URL` for remote runs |

See [staging-secrets-matrix.md](ops/staging-secrets-matrix.md) for staging values.

## PyPI package publish (S014 / EV-010 / F12–F14; EMPIRIC2 cutover EV-028 / #781)

Library packages publish **independently** of Render via GitHub Actions **OIDC trusted
publishing** on version tags:

| Package | Tag pattern | PyPI name |
|---------|-------------|-----------|
| `packages/tac-validate` | `tac-validate-v*` | `tac-validate` |
| `packages/iwxxm-validate` | `iwxxm-validate-v*` | `iwxxm-validate` |
| `packages/tac2iwxxm` | `tac2iwxxm-v*` | `tac2iwxxm` |

**First release**: `0.1.0` for each (bootstrap). **Subsequent releases** (e.g. `0.1.1`, EV-028):
bump `pyproject.toml` version, tag `{name}-v{version}`, workflow publishes via OIDC.

**One** GitHub Actions workflow (`.github/workflows/pypi-publish.yml`) with a **package matrix**
builds sdist+wheel (maturin manylinux/macOS/win for native crates), optional smoke-install,
then publishes on matching version tags. Prefer no long-lived `PYPI_API_TOKEN` when OIDC is
available.

**Trusted Publisher** (each PyPI project → Publishing settings):

| Field | Value |
|-------|--------|
| Owner | `EMPIRIC2` |
| Repository | `TAC-to-IWXXM` |
| Workflow | `pypi-publish.yml` |
| Environment | `pypi` |

Remove any stale publisher pointing at the pre-transfer GitHub owner/repo. Ensure GitHub
Environment `pypi` exists on `EMPIRIC2/TAC-to-IWXXM`. Workflow needs `id-token: write`
(see config-spec §F11–F14).

**Public landing pages**: Package `README.md` (and `pyproject.toml` `description`) are the
PyPI long/short description — write for library consumers; do not require internal ADR /
feature-id / execution-plan identifiers. Monorepo tracing stays in corpus / session docs.

**Render**: PyPI publish does not replace Render smokes. When msgspec **response** shapes
change, redeploy API then frontend and run H4–H5 + UJ-022.

## References

- `render.yaml` — Render Blueprint (API + static frontend)
- [staging-secrets-matrix.md](ops/staging-secrets-matrix.md) — staging env values
- [user-journeys.md](user-journeys.md) UJ-OPS-001, UJ-023
- [config-spec.md](config-spec.md) §F11–F14
- [ADR-026](adr/ADR-026-msgspec-http-openapi.md)
- Legacy three-service docs: [ARCHIVE/pre-monorepo-deploy/](ARCHIVE/pre-monorepo-deploy/)
