# TAC to IWXXM

[![CI/CD](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/ci-cd.yml)
[![E2E](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/e2e-tests.yml)

Convert aviation TAC (METAR, SPECI, TAF, SIGMET family, and related products) to WMO IWXXM XML.

The checkout is a React frontend, a FastAPI backend, a near-real-time ingest worker, and publishable Python packages. One git repository. No submodules.

**Staging:** https://app.staging.tac-to-iwxxm.com · https://api.staging.tac-to-iwxxm.com  
**Production:** https://app.tac-to-iwxxm.com · https://api.tac-to-iwxxm.com

## Install

```bash
git clone https://github.com/EMPIRIC2/TAC-to-IWXXM.git
cd TAC-to-IWXXM

# macOS system deps (python@3.12, node@22, uv, rust, …) — see Brewfile
brew bundle --file=Brewfile

cp .env.example .env   # add Supabase + DB credentials as needed
make install           # uv sync + pnpm install
```

## Run

```bash
make dev               # API on :8001, frontend on :5173
```

Open http://localhost:5173.

Docker Compose:

```bash
docker compose up --build
# Frontend http://localhost:18000  ·  API http://localhost:18001
```

Compose includes PostgreSQL (`db`) for local API tables. Auth and cloud work history still need Supabase credentials in `.env`.

In the app: paste or upload TAC, choose the IWXXM version, convert, validate, and download the XML. Sign in to keep server-side history. Some deployments offer send destinations after convert. Those controls are marked beta. Feedback: [GitHub Issues (`beta-feedback`)](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new?labels=beta-feedback).

Operator notes:

- [One-pager](docs/guides/operator-one-pager.md)
- [Handbook](docs/guides/operator-handbook.md)

Help in the converter header opens the one-pager.

## Layout

```
apps/backend/          FastAPI — /api/v1/* and /auth/*
apps/frontend/         React + Vite operator UI
apps/worker/           near-real-time ingest
apps/e2e/              Playwright
packages/tac2iwxxm/    TAC → IWXXM
packages/tac-validate/ TAC lint
packages/iwxxm-validate/ XSD + Schematron
packages/auth/         Supabase JWT middleware
packages/dissemination/ destination sinks
vendor/schemas/        read-only IWXXM schema snapshots
```

## Tests

```bash
make test-unit
make test-e2e-playwright-smoke
make tests:e2e
```

Live checks against a deployed API are in [docs/deploy.md](docs/deploy.md).

## Stack

| Layer | Stack |
|-------|--------|
| Frontend | React 18, TypeScript, Vite 6, Tailwind, Vitest |
| API | FastAPI, Python 3.12, uv workspace |
| Worker | Python poller → DO Postgres |
| Auth | Supabase Auth (via `packages/auth`) |
| Conversion | `tac2iwxxm` |
| Lint / validate | `tac-validate`, `iwxxm-validate` |
| E2E | Playwright |
| Deploy | DOKS |

## More

| Doc | What it is |
|-----|------------|
| [docs/ops/DEVELOPMENT.md](docs/ops/DEVELOPMENT.md) | Setup, env, local troubleshooting |
| [docs/deploy.md](docs/deploy.md) | Deploy and connectivity |
| [docs/guides/API.md](docs/guides/API.md) | Where the HTTP reference lives |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Release notes |

## License

MIT. See [LICENSE](LICENSE).
