# METAR to IWXXM Converter

[![CI/CD](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/ci-cd.yml)
[![E2E](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/e2e-tests.yml)
[![E2E tests](https://img.shields.io/badge/E2E_tests-64-blue)](apps/e2e)
[![Unit coverage gate](https://img.shields.io/badge/unit_coverage-%E2%89%A598%25-success)](docs/test-plan.md)

Convert aviation METAR/SPECI TAC messages to WMO IWXXM XML. React frontend, FastAPI backend,
and the in-repo [GIFTs](packages/gifts) library — all in a single git monorepo (no submodules).

## Features

- User registration and login via Supabase (auth routes on the API at `/auth/*`)
- Drag-and-drop or paste METAR/SPECI TAC input
- Batch conversion to IWXXM XML with copy, download, and ZIP export
- IWXXM version selection (vendor snapshots under `vendor/schemas/`)
- XSD and Schematron validation endpoints

## Architecture

Two deployables: **static frontend** + **API** (conversion, validation, and auth).

```
Browser
   │
   ▼
apps/frontend          Vite dev :5173  ·  Docker :18000
   │  VITE_API_BASE_URL
   ▼
apps/backend           :8001 (dev)  ·  :18001 (Docker)
   ├── packages/auth    Supabase JWT + /auth/* routes
   ├── packages/gifts   TAC → IWXXM
   └── vendor/schemas   read-only wmo-im snapshots
```

**Developer guide:** [docs/ops/DEVELOPMENT.md](docs/ops/DEVELOPMENT.md)  
**Deployment:** [docs/deploy.md](docs/deploy.md)

## Quick start

```bash
git clone https://github.com/EMPIRIC2/TAC-to-IWXXM.git
cd TAC-to-IWXXM

cp .env.example .env   # add Supabase credentials
make install           # uv sync + pnpm install
make dev               # API on :8001, frontend on :5173
```

Open http://localhost:5173. With Docker Compose instead:

```bash
docker compose up --build
# Frontend http://localhost:18000  ·  API http://localhost:18001
```

Docker Compose ships a bundled PostgreSQL service (`db`), so the stack is
self-contained out of the box — no external database is required for the API to
start. The backend defaults `DATABASE_URL` to that service; override it in `.env`
(e.g. a Supabase pooler URL) to point at another database. Auth and work-history
(F5) still require Supabase credentials in `.env` — the bundled Postgres only
backs the ORM tables (statistics/evaluation), not Supabase auth/RLS.

## Project structure

```
metar-to-IWXXM/
├── apps/
│   ├── backend/       # FastAPI — /api/v1/* and /auth/*
│   ├── frontend/      # React + Vite
│   └── e2e/           # Playwright suites
├── packages/
│   ├── auth/          # Auth library (mounted in backend)
│   ├── gifts/         # IWXXM conversion
│   └── shared/        # Shared types and constants
├── vendor/schemas/    # Read-only iwxxm snapshots (sync via make vendor-sync)
├── tests/             # Migration gates, integration, smoke
├── docs/              # Specs, deploy runbook, development guide
├── Makefile
└── docker-compose.yml # db (Postgres) + backend + frontend
```

## Testing

```bash
make test-unit              # Workspace unit tests (Python + shared TS)
make test-e2e-playwright-smoke   # Playwright smoke (no admin credentials)
make tests:e2e              # Full Playwright suite (apps/e2e)
```

Coverage gate: **95%** on all packages and apps. See [docs/test-plan.md](docs/test-plan.md).

### Live tests (Render T3 — manual)

Populate `.env` with `LIVE_API_URL`, `LIVE_FRONTEND_URL`, and admin credentials, then:

```bash
make test-live-connectivity   # H4–H5 CORS + bundle
make test-live-api            # H3 live API pytest
make test-live-e2e            # H6 Playwright UJ-001–003
make test-live                # All tiers (pre-release signoff)
```

See [docs/deploy.md](docs/deploy.md) §Live test harness. Requires E2E-001 schema path fix for full validation coverage.

## Key technologies

| Layer | Stack |
|-------|--------|
| Frontend | React 18, TypeScript, Vite 6, Tailwind, Vitest |
| API | FastAPI, Python 3.12, uv workspace |
| Auth | Supabase (via `packages/auth`) |
| Conversion | GIFTs (`packages/gifts`) |
| E2E | Playwright |
| Deploy | Render — Docker API + static frontend |

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/ops/DEVELOPMENT.md](docs/ops/DEVELOPMENT.md) | Setup, env vars, troubleshooting |
| [docs/deploy.md](docs/deploy.md) | Render topology and connectivity runbook |
| [docs/api-contract.md](docs/api-contract.md) | HTTP API reference |
| [docs/spec.md](docs/spec.md) | Technical specification |
| [docs/feature-list.md](docs/feature-list.md) | Product features |

## License

MIT — see [LICENSE](LICENSE).
