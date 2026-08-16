# TAC to IWXXM

[![CI/CD](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/ci-cd.yml)
[![E2E](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/e2e-tests.yml)
[![E2E tests](https://img.shields.io/badge/E2E_tests-87-blue)](apps/e2e)
[![Unit coverage gate](https://img.shields.io/badge/unit_coverage-%E2%89%A595%25-success)](docs/test-plan.md)

Convert aviation TAC (METAR, SPECI, TAF, SIGMET family, and related products) to WMO IWXXM
XML. React frontend, FastAPI backend, near-RT ingest worker, and publishable Python packages —
all in a single git monorepo (no submodules).

## Features

- Public convert workbench (guest mode) with optional Auth for saved history
- Multi-product TAC → IWXXM via [`tac2iwxxm`](packages/tac2iwxxm/)
- TAC lint ([`tac-validate`](packages/tac-validate/)) and IWXXM XSD + Schematron
  ([`iwxxm-validate`](packages/iwxxm-validate/))
- Soft preview / decode summaries and workbench lint UX
- **Quality metrics** tab — compare converted IWXXM to the official WMO example corpus
  (`/quality`, shareable `/quality/:stem`)
- Near-real-time ingest worker
- Dissemination sink APIs retained (operator UI destinations currently hidden — restore tracked separately)

## Architecture

Three deployables on **DigitalOcean Kubernetes (DOKS)**: static frontend, API, and worker.
Auth is Supabase Auth-only (JWT on the API). Product data uses DO Postgres.

```
Browser
   │
   ▼
apps/frontend          Vite :5173  ·  Docker :18000
   │  VITE_API_BASE_URL / runtime /config.json
   ▼
apps/backend           :8001 (dev)  ·  :18001 (Docker)
   ├── packages/auth           Supabase JWT + /auth/*
   ├── packages/tac2iwxxm      TAC → IWXXM
   ├── packages/tac-validate   TAC lint
   ├── packages/iwxxm-validate XSD + Schematron
   ├── packages/dissemination  sink adapters (API-mediated)
   └── vendor/schemas          read-only wmo-im + iwxxm-us snapshots

apps/worker            near-RT ingest → DO Postgres
```

**Staging:** https://app.staging.tac-to-iwxxm.com · https://api.staging.tac-to-iwxxm.com  
**Production:** https://app.tac-to-iwxxm.com · https://api.tac-to-iwxxm.com  

**Developer guide:** [docs/ops/DEVELOPMENT.md](docs/ops/DEVELOPMENT.md)  
**Deployment:** [docs/deploy.md](docs/deploy.md) · [docs/deploy-state.md](docs/deploy-state.md)

## Quick start

```bash
git clone https://github.com/EMPIRIC2/TAC-to-IWXXM.git
cd TAC-to-IWXXM

# macOS system deps (python@3.12, node@22, uv, rust, …) — see Brewfile
brew bundle --file=Brewfile

cp .env.example .env   # add Supabase + DB credentials as needed
make install           # uv sync + pnpm install
make dev               # API on :8001, frontend on :5173
```

Open http://localhost:5173. With Docker Compose instead:

```bash
docker compose up --build
# Frontend http://localhost:18000  ·  API http://localhost:18001
```

**Operator docs** (convert → validate → download):

- [Operator one-pager](docs/guides/operator-one-pager.md) — one printed page
- [Operator handbook](docs/guides/operator-handbook.md) — login, history, Quality metrics, ingest, troubleshooting

In the app, use **Help** in the converter header (same one-pager).

Docker Compose ships a bundled PostgreSQL service (`db`), so the stack is
self-contained out of the box for local API/ORM tables. Auth and cloud work-history
still need Supabase credentials in `.env` when you exercise those paths.

## Project structure

```
TAC-to-IWXXM/
├── apps/
│   ├── backend/       # FastAPI — /api/v1/* and /auth/*
│   ├── frontend/      # React + Vite operator UI
│   ├── worker/        # near-RT ingest
│   └── e2e/           # Playwright suites
├── packages/
│   ├── auth/          # Supabase Auth JWT middleware
│   ├── tac2iwxxm/     # TAC → IWXXM (PyPI)
│   ├── tac-validate/  # TAC lint (PyPI)
│   ├── iwxxm-validate/# XSD + Schematron (PyPI)
│   ├── dissemination/ # destination sinks / SSRF helpers
│   └── shared/        # Shared types and constants
├── vendor/schemas/    # Read-only iwxxm snapshots (make vendor-sync)
├── deploy/doks/       # Staging + prod overlays
├── tests/             # Migration gates, integration, smoke, bug repros
├── docs/              # Specs and guides — start at docs/CORPUS.md
├── Makefile
└── docker-compose.yml # db + backend + frontend (+ optional mocks)
```

## Testing

```bash
make test-unit              # Workspace unit tests (Python + shared TS)
make test-e2e-playwright-smoke   # Playwright smoke (no admin credentials)
make tests:e2e              # Full Playwright suite (apps/e2e)
```

Coverage gate: **≥95%** lines/statements/functions (and Vitest branches ≥95%). See
[docs/test-plan.md](docs/test-plan.md).

### Live / staging connectivity

Populate `.env` with staging or prod URLs and credentials as needed, then:

```bash
make test-live-connectivity   # H4–H5 CORS + bundle
make test-live-api            # H3 live API pytest
make test-live-e2e            # H6 Playwright journeys
make test-live                # All tiers (pre-release signoff)
```

See [docs/deploy.md](docs/deploy.md) §Live test harness.

## Key technologies

| Layer | Stack |
|-------|--------|
| Frontend | React 18, TypeScript, Vite 6, Tailwind, Vitest |
| API | FastAPI, Python 3.12, uv workspace |
| Worker | Python poller → DO Postgres |
| Auth | Supabase Auth (via `packages/auth`) |
| Conversion | `tac2iwxxm` (+ optional Rust/PyO3) |
| Lint / validate | `tac-validate`, `iwxxm-validate` |
| E2E | Playwright |
| Deploy | DOKS (staging from `stage`, prod from `main` / deploy tags) |

## Branch / release posture (current)

| Branch | Role | What’s live |
|--------|------|-------------|
| `stage` | Staging deploys | Quality metrics (list + detail pages) on staging; promote to production deferred |
| `main` | Production | Last production promote: 2026-08-10 |

Quality metrics on staging: https://app.staging.tac-to-iwxxm.com/quality

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/CORPUS.md](docs/CORPUS.md) | Canonical doc index |
| [docs/ops/DEVELOPMENT.md](docs/ops/DEVELOPMENT.md) | Setup, env vars, troubleshooting |
| [docs/deploy.md](docs/deploy.md) | DOKS topology and connectivity runbook |
| [docs/deploy-state.md](docs/deploy-state.md) | Current staging / prod tips |
| [docs/api-contract.md](docs/api-contract.md) | HTTP API reference |
| [docs/spec.md](docs/spec.md) | System specification |
| [docs/feature-list.md](docs/feature-list.md) | Product features |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Release notes |

## License

MIT — see [LICENSE](LICENSE).
