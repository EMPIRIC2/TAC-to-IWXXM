# TAC to IWXXM

[![CI/CD](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/ci-cd.yml)
[![E2E](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/workflows/e2e-tests.yml)

This repository turns aviation Traditional Alphanumeric Code (TAC) into
World Meteorological Organization (WMO) IWXXM XML.

TAC products covered include METAR (routine weather report), SPECI (special
METAR), TAF (terminal aerodrome forecast), the SIGMET family (significant
meteorological information), and related products.

The repository holds one React operator website, one FastAPI HTTP service, one
near-real-time ingest worker, and publishable Python packages. The repository
does not use Git submodules.

**Staging website:** https://app.staging.tac-to-iwxxm.com  
**Staging API:** https://api.staging.tac-to-iwxxm.com  
**Production website:** https://app.tac-to-iwxxm.com  
**Production API:** https://api.tac-to-iwxxm.com

## Install

```bash
git clone https://github.com/EMPIRIC2/TAC-to-IWXXM.git
cd TAC-to-IWXXM

# macOS system packages (python@3.12, node@22, uv, rust, and more) — see Brewfile
brew bundle --file=Brewfile

cp config/env.example .env   # add Supabase and database credentials as needed
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

Compose starts PostgreSQL (`db`) for local API tables. Authentication and cloud
work history still need Supabase credentials in `.env`.

In the operator website: paste or upload TAC, choose the IWXXM release line,
convert, validate, and download the XML. Sign in to keep server-side work
history. Some deployments show send destinations after convert. Those send
controls are marked beta. Send feedback through
[GitHub Issues with the `beta-feedback` label](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new?labels=beta-feedback).

Operator notes:

- [One-pager](docs/guides/operator-one-pager.md)
- [Handbook](docs/guides/operator-handbook.md)

The Help control in the converter header opens the one-pager.

## Layout

```
apps/backend/            FastAPI — /api/v1/* and /auth/*
apps/frontend/           React + Vite operator website
apps/worker/             near-real-time ingest poller
apps/e2e/                Playwright end-to-end tests
packages/tac2iwxxm/      TAC → IWXXM conversion library
packages/tac-validate/   TAC lint (business-rule checks)
packages/iwxxm-validate/ XSD + Schematron validation
packages/auth/           Supabase JWT middleware
packages/dissemination/  destination send adapters
vendor/schemas/          read-only IWXXM schema snapshots
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
| Operator website | React 18, TypeScript, Vite 6, Tailwind, Vitest |
| HTTP API | FastAPI, Python 3.12, uv workspace |
| Ingest worker | Python poller that writes to DigitalOcean Postgres |
| Authentication | Supabase Auth through `packages/auth` |
| Conversion | `tac2iwxxm` |
| Lint / validate | `tac-validate`, `iwxxm-validate` |
| End-to-end tests | Playwright |
| Deploy | DigitalOcean Kubernetes Service (DOKS) |

## More

| Doc | What it is |
|-----|------------|
| [docs/ops/DEVELOPMENT.md](docs/ops/DEVELOPMENT.md) | Setup, environment variables, local troubleshooting |
| [docs/deploy.md](docs/deploy.md) | Deploy and connectivity |
| [docs/guides/API.md](docs/guides/API.md) | Where the HTTP API reference lives |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Release notes |

## License

MIT. See [LICENSE](LICENSE).
