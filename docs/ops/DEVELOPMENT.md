# Development Guide

Complete setup, local development, and testing for the TAC to IWXXM monorepo.

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.12 | Pinned in root `pyproject.toml` / `.python-version` |
| Node.js | 22 | Pinned in `.nvmrc` / CI |
| [uv](https://docs.astral.sh/uv/) | latest | Python workspace install |
| [pnpm](https://pnpm.io/) | `pnpm@9.15.4` via corepack | From root `package.json` `packageManager` — do not brew-install pnpm |
| Rust (cargo/rustc) | ≥1.74 | Native maturin builds (ADR-017); Homebrew `rust` in Brewfile |
| Docker (optional) | Compose v2 | Local stack: db + backend + frontend |
| Supabase project | — | Auth (Auth-only); product DB is DO Postgres in staging/prod |

**macOS:** install system deps from the root [`Brewfile`](../../Brewfile) (exact formulae +
verified bottle versions in comments):

```bash
brew bundle --file=Brewfile
```

Then `make install` (uv + corepack pnpm). Vendor schemas ship in-repo — a plain `git clone`
is all you need for schema assets.

## Quick start (local)

```bash
git clone https://github.com/EMPIRIC2/TAC-to-IWXXM.git
cd TAC-to-IWXXM

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
apps/backend/            FastAPI — conversion, validation, /auth/*, dissemination
apps/frontend/           React operator UI (incl. Quality metrics /quality)
apps/worker/             near-RT ingest poller
apps/e2e/                Playwright tests
packages/auth/           Supabase Auth JWT middleware (library, not a deployable)
packages/tac2iwxxm/      TAC → IWXXM (PyPI)
packages/tac-validate/   TAC lint (PyPI)
packages/iwxxm-validate/ XSD + Schematron (PyPI)
packages/dissemination/  destination sink adapters / SSRF helpers
packages/shared/         Shared Python/TS types
vendor/schemas/          Read-only wmo-im + iwxxm-us snapshots
deploy/doks/             Staging + prod Kubernetes overlays
tests/                   Migration gates, smoke, integration, bug repros
```

`packages/gifts` was removed at the general TAC→IWXXM cutover. Do not reintroduce GIFTs paths.

## Architecture

```
┌─────────────────┐     VITE_API_BASE_URL      ┌──────────────────────────────┐
│ apps/frontend   │ ─────────────────────────► │ apps/backend                 │
│ (React + Vite)  │     /api/v1/*  /auth/*     │  ├─ packages/auth             │
└─────────────────┘                            │  ├─ packages/tac2iwxxm        │
                                               │  ├─ packages/tac-validate     │
                                               │  ├─ packages/iwxxm-validate   │
                                               │  ├─ packages/dissemination    │
                                               │  └─ vendor/schemas            │
                                               └───────────┬──────────────────┘
                     apps/worker (ingest)                 │
                           │                              ▼
                           └──────────────► DO Postgres · Supabase Auth
```

Auth endpoints (`/auth/register`, `/auth/login`, `/auth/me`, …) live on the same host
as conversion APIs. The frontend uses a single `VITE_API_BASE_URL` (or runtime
`/config.json`) for both.

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
make openapi-refresh  # Dump FastAPI OpenAPI + regenerate FE types (EV-052)
# Drift check: pnpm --filter @metar/frontend run openapi:check
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

# Package unit examples
cd packages/tac2iwxxm && uv run pytest tests/ -v
cd packages/tac-validate && uv run pytest tests/ -v
cd packages/iwxxm-validate && uv run pytest tests/ -v
```

## Testing

### Unit tests

```bash
make test-unit
```

Runs migration smoke tests, root `tests/unit/`, and `packages/shared` with 95% coverage
gate.

### Backend / package coverage

```bash
make test-unit-backend    # apps/backend
# Prefer workspace: make test-unit
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

Primary workflow: `.github/workflows/ci-cd.yml` (**EV-036** local-first amend).

| Tier | Where | What |
|------|-------|------|
| Lint (EV-047) | husky **pre-commit** | `make lint-fast` — ruff / prettier / eslint only. |
| Fast units (EV-047) | husky **pre-push** | `make test-unit-fast` — workspace + tac2iwxxm units (not Compose / not validate-ci). |
| Opt-in full local | `make` | `validate-ci` / `ci-prepush` / `make ci` (units + Compose on **18000/18001**) when you want full parity. |
| Remote PR/push | GitHub Actions | **No** `validate` job; **no** Compose integration. **Keeps** package **unit matrix** + coverage + sticky **PR coverage comment** + sticky **quality/golden PR comment** (EV-052). Also `rust-crates` / `Rust crates (fmt/clippy/test)` gate, `tac2iwxxm-native` maturin matrix (both packages), `e2e-smoke`, `test-alembic` (EV-045). |
| Deploy | `main`/`stage` push | needs `test` + `test-alembic` + `rust-crates-gate` + `tac2iwxxm-native`; GHCR + DOKS |

Image deploys use `scripts/deploy/trigger_render_image_deploy.py` (hook + `imgURL`, with REST
`imageUrl` fallback when `RENDER_API_KEY` is set — BUG-2026-08-03).

| Job | Checks |
|-----|--------|
| **test** (matrix) | Package unit tests with coverage (`--cov-fail-under` / Vitest) |
| **coverage-pr-comment** | Sticky PR comment from coverage XML / Vitest summary (PRs only) |
| **quality-pr-comment** | Sticky PR comment #2: quality-matrix + annex3/`iwxxm_us` golden outcomes by product × profile (PRs only; EV-052) |
| **rust-crates** / **rust-crates-gate** | fmt + clippy `-D warnings` + `cargo test` both crates; gate name `Rust crates (fmt/clippy/test)` |
| **tac2iwxxm-native** | PyO3 / maturin matrix (`tac2iwxxm` + `iwxxm-validate` display names) |
| **make rust-check** | Local mirror of rust crates + both native smokes |
| **e2e-smoke** | Playwright smoke |
| **test-alembic** | Alembic upgrade head (TC-EV031-002) |
| **deploy** | Docker build/push + DOKS (`stage` / `main` / deploy tags; skipped if CD credentials incomplete) |

Local gates:

```bash
make install-hooks    # husky (.husky/*) + pre-commit hook environments
make lint-fast        # husky pre-commit default (EV-047)
make test-unit-fast   # husky pre-push default (EV-047)
make pre-commit-run   # opt-in: all-files pre-commit + validate-ci-medium
make pre-push-run     # same as husky pre-push (test-unit-fast)
make validate-fast    # format/lint/typecheck/secrets/yaml/catalog
make validate-ci-medium  # config-guard + env-check + audit-frontend
make validate-ci      # validate-fast + validate-ci-medium (manual full local validate)
make ci-prepush       # unit/matrix suite (no Compose)
make ci               # ci-prepush + test-integration (needs ports 18000/18001)
make test-ev032-a6-2-canary         # EV-032 #835 A6-2 equality + catalog (pre-commit canary)
make test-ev032-vona-canary         # EV-032 #741 VONA ADR-032 + product=vona (pre-commit canary)
make test-tc-sigmet-quality         # TC SIGMET long pack (includes #835 A6-2 deepen)
make test-vona-quality              # VONA long pack (lint → convert → validate + API enum)
```

Hooks (after `make install-hooks`; husky sets `core.hooksPath=.husky`; **EV-047**):

| Git hook | Runs |
|----------|------|
| **pre-commit** | `make lint-fast` (ruff / prettier / eslint only) |
| **pre-push** | `make test-unit-fast` (workspace + tac2iwxxm units) |

Heavier gates (typecheck, catalog/registry, actionlint/yamllint, medium validate, full
unit matrix, Compose) stay on **remote CI** and opt-in `make validate-*` / `ci-prepush` /
`make ci`. Family long packs (`make test-*-quality`) stay opt-in / path-filtered.

Bypass only when intentional: `git commit --no-verify` / `git push --no-verify`.
Do **not** use `--no-verify` as a merge path for `main` / `stage` — remote CI must stay green.

- Python 3.12 + Node 22
- Unit coverage gates enforced in CI (`test` job) and locally via husky / `make ci-prepush`
- Builds API Docker image from repo root context (when CD credentials present)
- Builds frontend static assets from `apps/frontend`

Removed from remote CI (EV-036): standalone **validate** job and Compose **integration**
matrix entry (moved to local hooks). Historical merges into validate (EV-002): `secret-scan.yml`,
`github-yaml-lint.yml`, `frontend-audit.yml` — still covered by local `validate-fast` / medium.

Vendor schemas: weekly GitHub Action syncs wmo-im repos into `vendor/schemas/` (see
`scripts/vendor/sync-iwxxm.sh`).

### Converter PR perf baselines (EV-047 / #834)

Committed baselines: `tests/perf/baselines/converter_pr.yaml` (`status: ci_recorded`).
CI job **`Converter perf (tac2iwxxm)`** hard-fails when convert-only p95 exceeds
`max(baseline×1.20, baseline+200µs)`.

```bash
make test-converter-pr-gate                          # run the gate locally
make perf-converter-baseline HOST=ubuntu-latest STATUS=ci_recorded   # intentional refresh
```

Do **not** bump ceilings by editing YAML after a red gate without measuring on a
Linux/CI-class host. Husky does **not** run this gate (CI-only).

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

**Primary:** DigitalOcean Kubernetes (DOKS) — staging from `stage`, production from `main`
/ deploy tags (`vYYYY.MM.DD-deploy`). See [deploy.md](../deploy.md) and
[deploy-state.md](../deploy-state.md) for topology, env vars, and connectivity checks
(H0c–H5). Render services are legacy/suspended.

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
