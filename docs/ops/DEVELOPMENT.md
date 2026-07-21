# Development Guide

Complete setup, local development, and testing for the METAR to IWXXM monorepo.

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.12 | Pinned in root `pyproject.toml` |
| Node.js | 22 | Pinned in `.nvmrc` / CI |
| [uv](https://docs.astral.sh/uv/) | latest | Python workspace install |
| [pnpm](https://pnpm.io/) | via corepack | JavaScript workspace |
| Docker (optional) | Compose v2 | Local stack: db + backend + frontend |
| Supabase project | — | Auth and optional Postgres |

Vendor schemas ship in-repo — a plain `git clone` is all you need.

## Quick start (local)

```bash
git clone https://github.com/joseph-c-mcguire/metar-to-IWXXM.git
cd metar-to-IWXXM

cp .env.example .env
# Edit .env: SUPABASE_PUBLISHABLE_KEY, SUPABASE_SECRET_KEY, DATABASE_URL (see config-spec.md)

export METAR_CONFIG_ENV=local
make install
make dev
```

| Service | URL (default) |
|---------|----------------|
| Frontend (Vite) | http://localhost:18000 |
| API (backend + auth) | http://localhost:18001 |
| API docs | http://localhost:8001/docs |
| Auth routes | http://localhost:8001/auth/* |

`make dev` runs `./start-dev-servers.sh`, which starts the merged API from `apps/backend`
and the Vite dev server from `apps/frontend`.

## Quick start (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

| Service | URL (default) |
|---------|----------------|
| Frontend | http://localhost:18000 |
| API | http://localhost:18001 |

Compose runs **db (Postgres) + backend + frontend** — auth is inlined in the API
image via `packages/auth`. The bundled `db` service makes the stack self-contained:
the backend defaults `DATABASE_URL` to it, so `docker compose up` starts without an
external database. Override `DATABASE_URL` in `.env` to point at another Postgres
(e.g. a Supabase pooler). The bundled Postgres only backs the ORM tables
(statistics/evaluation) — auth and work-history (F5) still need Supabase
credentials in `.env`.

## Repository layout

```
apps/backend/     FastAPI app — conversion, validation, /auth/*
apps/frontend/    React UI
apps/e2e/         Playwright tests
packages/auth/    Supabase middleware (library, not a deployable)
packages/gifts/   TAC → IWXXM conversion
packages/shared/  Shared Python/TS types
vendor/schemas/   Read-only wmo-im XSD snapshots
tests/            Migration gates (TC-M001–M005), smoke, integration
```

Legacy top-level `backend/`, `frontend/`, `auth/`, and `GIFTs/` trees may still exist
during transition; **new work targets `apps/` and `packages/` only**.

## Architecture

```
┌─────────────────┐     VITE_API_BASE_URL      ┌──────────────────────────┐
│ apps/frontend   │ ─────────────────────────► │ apps/backend             │
│ (React + Vite)  │     /api/v1/*  /auth/*     │  ├─ packages/auth        │
└─────────────────┘                            │  ├─ packages/gifts       │
                                               │  └─ vendor/schemas       │
                                               └───────────┬──────────────┘
                                                           │
                                                           ▼
                                                    Supabase (remote)
```

Auth endpoints (`/auth/register`, `/auth/login`, `/auth/me`, …) live on the same host
as conversion APIs. The frontend uses a single `VITE_API_BASE_URL` for both.

## Environment variables

Copy `.env.example` to `.env` at the repo root — **secrets only** (five placeholders).
Non-secret URLs, CORS, and feature flags live in `config/local.json` or `config/prod.json`,
selected by `METAR_CONFIG_ENV` (default `local`).

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_PUBLISHABLE_KEY` | Yes | `sb_publishable_*` — client + server JWT validation |
| `SUPABASE_SECRET_KEY` | Yes | `sb_secret_*` — Auth Admin API (`create_admin_user.py` only) |
| `DATABASE_URL` | Local: no¹ / Prod: yes | Postgres URL (evaluation jobs, statistics). ¹Under Docker Compose, leave blank to use the bundled `db` service; a blank value is treated as unset. |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Local | Operator bootstrap user |
| `METAR_CONFIG_ENV` | No | `local` (default) or `prod` |

**Deprecated** (one-release shim): `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`,
`VITE_*`, `METAR_CORS_ORIGINS`, `DISABLE_AUTH`, `FRONTEND_URL`.

Verify alignment: `make env-check`. Operator sync: [env-sync-runbook.md](env-sync-runbook.md),
[env-contract.md](../env-contract.md).

### Supabase local stack (optional)

Schema migrations live at **`supabase/migrations/`** (timestamp-ordered) with
`supabase/seed.sql`, following [Supabase local development](https://supabase.com/docs/guides/local-development/overview).

```bash
npm install -g supabase    # or see Supabase CLI docs
make supabase-start        # Docker required
make supabase-reset        # apply migrations + seed
make supabase-status       # local URL + keys for .env
```

For local auth testing, point `config/local.json` → `supabase.url` to `http://127.0.0.1:54321`
and copy publishable/secret keys from `make supabase-status`. Production push:
`supabase link --project-ref ktvxijislbtgqapllmuk` then `make supabase-push`.

RLS advisor migrations (004–006) target METAR tables only — see env-sync-runbook §Database advisor.

## Workspace commands

```bash
make install          # uv sync + pnpm install
make dev              # Start API + Vite (interactive port cleanup)
make dev-kill         # Same, auto-kill conflicting ports
make test-unit        # Python workspace + packages/shared tests
make vendor-sync      # Refresh vendor/schemas from wmo-im manifest
```

### Per-package development

```bash
# API only
cd apps/backend
uv run uvicorn src.api:app --reload --host 0.0.0.0 --port 18001

# Frontend only
cd apps/frontend
METAR_CONFIG_ENV=local bash ../../scripts/frontend/prepare-config.sh
pnpm dev --host 0.0.0.0 --port 18000

# GIFTs tests
cd packages/gifts && uv run pytest tests/ -v
```

## Testing

### Unit tests

```bash
make test-unit
```

Runs migration smoke tests, root `tests/unit/`, and `packages/shared` with 95% coverage
gate.

### Backend / package coverage (legacy paths still supported)

```bash
make test-unit-backend    # apps/backend via legacy Makefile target
make test-unit-gifts
```

Prefer `make test-unit` for CI-aligned workspace checks.

### Integration and smoke

```bash
pytest tests/unit/test_cors_policy.py -v          # H0c CORS policy
pytest apps/backend/tests/integration/ -v         # H0i connectivity
pytest tests/smoke/ -v                            # Staging smoke (offline subset)
```

### E2E (Playwright)

Specs live in `apps/e2e/`. `make dev` or Docker must be running for full-stack tests.

| Target | Credentials | Scope |
|--------|-------------|-------|
| `make test-e2e-playwright-smoke` | None | Health, auth integration, mocked conversion |
| `make test-e2e-t2-product` | Admin optional | TC-001 + TC-003 product gate |
| `make tests:e2e` | Admin for login flows | Full suite |

Playwright env vars:

- `PLAYWRIGHT_ADMIN_EMAIL`, `PLAYWRIGHT_ADMIN_PASSWORD` — required for admin login specs
- `PLAYWRIGHT_TAC_FIXTURES_DIR` — override TAC fixture directory
- `PLAYWRIGHT_REQUIRE_TAC_FIXTURES=1` — fail if fixtures missing (CI default)

## CI/CD

Primary workflow: `.github/workflows/ci-cd.yml` (EV-002: **validate → test → deploy** on push to
`main`; PRs run validate + test only).

| Job | Checks |
|-----|--------|
| **validate** | `make validate-ci` — format, lint, typecheck, gitleaks, actionlint/yamllint, config-guard, frontend npm audit |
| **test** | Matrix: shared, backend, auth, gifts, frontend, integration — pytest 98% + Codecov 95% |
| **deploy** | Docker build/push + Render hooks (`main` push only) |

Local gates (dual-run with CI validate + test):

```bash
make install-hooks    # installs pre-commit + pre-push hooks
pre-commit run --all-files          # fast commit gates
make pre-push-run                   # make validate-ci + make ci-prepush (same as git push)
make validate-fast                  # format/lint/typecheck/secrets/yaml/catalog
make validate-ci                    # CI validate job locally
make ci-prepush                     # unit/matrix suite (no Compose)
make ci                             # ci-prepush + test-integration (needs ports 18000/18001)
```

Hooks (after `make install-hooks`):

| Git hook | Runs |
|----------|------|
| **pre-commit** | gitleaks, ruff, prettier, eslint, tsc, basedpyright, catalog + issue-registry, actionlint/yamllint |
| **pre-push** | `make validate-ci` then `make ci-prepush` (blocks push if CI validate/unit would fail) |

Bypass only when intentional: `git commit --no-verify` / `git push --no-verify`.
Also update `ci-quality-guard.sh` message if it mentions make ci.

- Python 3.12 + Node 22
- Unit tests and 95% Codecov gate on `apps/backend`, `packages/*`, `apps/frontend`
- Builds API Docker image from repo root context
- Builds frontend static assets from `apps/frontend`

Removed standalone PR workflows (merged into `ci-cd.yml` validate): `secret-scan.yml`,
`github-yaml-lint.yml`, `frontend-audit.yml`.

Vendor schemas: weekly GitHub Action syncs wmo-im repos into `vendor/schemas/` (see
`scripts/vendor/sync-iwxxm.sh`).

## Troubleshooting

### `make install` fails

Ensure uv and corepack are available:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
corepack enable
make install
```

### Port already in use

```bash
make dev-kill
# or: ./start-dev-servers.sh --kill
```

Default dev ports: **8001** (API), **5173** (frontend). Docker Compose uses **18001** /
**18000**.

### CORS errors in the browser

- Confirm API is running and `METAR_CORS_ORIGINS` includes your frontend origin
- Local Vite: `METAR_CORS_ORIGINS=http://localhost:5173`
- Check `pytest tests/unit/test_cors_policy.py`

### Module not found (Python)

Run from repo root after `uv sync`:

```bash
uv run pytest tests/migration/test_workspace_import_smoke.py -v
```

### Frontend cannot reach API

Verify `VITE_API_BASE_URL` in `.env` matches the running API port (8001 local, 18001
Docker).

## Deployment

Production uses **two Render services** (API + static frontend). See [deploy.md](../deploy.md)
for topology, env vars, and post-deploy connectivity checks (H4/H5).

## Agent workflow (pipeline sessions)

Cursor pipeline skills (00–19) use a **session-first** model for all bounded work — from
greenfield builds to feature adds, hotfixes, and live E2E integration.

1. Invoke **00-context** with your goal (e.g. “add export API”, “run live E2E on staging”).
2. 00 classifies the session type, allocates `S001-{slug}`, and proposes `routing-plan.md`.
3. Approve the plan → `active_session` is set in `workflow-state.yaml`.
4. Run stages listed in the plan; reports land in `docs/sessions/SNNN-slug/reports/`.
5. Close the session when all plan stages complete (checkpoint AskQuestion).

| Doc | Purpose |
|-----|---------|
| [skill-routing.md](../skill-routing.md) | Which skill to invoke |
| [sessions/README.md](../sessions/README.md) | Session index and folder layout |
| [context/README.md](../context/README.md) | Scoped context briefs |

Skill reference: [.cursor/skills/sessions-reference.md](../../.cursor/skills/sessions-reference.md).

## Further reading

| Document | Topic |
|----------|-------|
| [skill-routing.md](../skill-routing.md) | Pipeline skill routing and session types |
| [sessions/README.md](../sessions/README.md) | Active and archived work sessions |
| [api-contract.md](../api-contract.md) | REST endpoints |
| [test-plan.md](../test-plan.md) | Test tiers and migration gates |
| [migration-plan.md](migration-plan.md) | Submodule → monorepo migration |
| [adr/ADR-002-auth-merged-into-backend.md](../adr/ADR-002-auth-merged-into-backend.md) | Auth merge decision |

Legacy three-service and submodule docs are in
[ARCHIVE/pre-monorepo-deploy/](../ARCHIVE/pre-monorepo-deploy/).
