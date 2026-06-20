# METAR to IWXXM Converter

[![CI/CD](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/workflows/ci-cd.yml)
[![E2E](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/workflows/e2e-tests.yml)
[![codecov](https://codecov.io/gh/joseph-c-mcguire/metar-to-IWXXM/graph/badge.svg)](https://codecov.io/gh/joseph-c-mcguire/metar-to-IWXXM)

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

**Developer guide:** [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)  
**Deployment:** [docs/deploy.md](docs/deploy.md)

## Quick start

```bash
git clone https://github.com/joseph-c-mcguire/metar-to-IWXXM.git
cd metar-to-IWXXM

cp .env.example .env   # add Supabase credentials
make install           # uv sync + pnpm install
make dev               # API on :8001, frontend on :5173
```

Open http://localhost:5173. With Docker Compose instead:

```bash
docker compose up --build
# Frontend http://localhost:18000  ·  API http://localhost:18001
```

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
└── docker-compose.yml # backend + frontend (two services)
```

## Testing

```bash
make test-unit              # Workspace unit tests (Python + shared TS)
make test-e2e-playwright-smoke   # Playwright smoke (no admin credentials)
make tests:e2e              # Full Playwright suite (apps/e2e)
```

Coverage gate: **95%** on all packages and apps. See [docs/test-plan.md](docs/test-plan.md).

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
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Setup, env vars, troubleshooting |
| [docs/deploy.md](docs/deploy.md) | Render topology and connectivity runbook |
| [docs/api-contract.md](docs/api-contract.md) | HTTP API reference |
| [docs/spec.md](docs/spec.md) | Technical specification |
| [docs/feature-list.md](docs/feature-list.md) | Product features |

## License

MIT — see [LICENSE](LICENSE).
