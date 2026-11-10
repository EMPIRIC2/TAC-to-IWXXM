# Ops contract

> Index: [README.md](README.md) 
> Env names: [env-variable.md](env-variable.md) 
> Last updated: 2026-11-10

This document states operational requirements for local run, staging, and
production. Long runbooks may stay in the local `docs/ops/` feeder.

## Terms

| Term | Meaning |
|------|---------|
| DOKS | DigitalOcean Kubernetes Service |
| BYOC | Bring Your Own Credentials for one dissemination send |
| Profile JSON | Non-secret runtime config under `deploy/profiles/` |

## Tooling bar

| Tool | Version / note |
|------|----------------|
| Python | 3.12 |
| Node.js | 22 |
| uv | Workspace install |
| pnpm | From root `packageManager` via corepack |
| Rust | Optional; needed for native maturin builds |
| Docker Compose | Optional local stack |

On macOS, install system packages from the root `Brewfile`, then run
`make install`.

## Local quick start

1. Copy `.env.example` to `.env`.
2. Set Auth keys and `DATABASE_URL` per [env-variable.md](env-variable.md).
3. Export `METAR_CONFIG_ENV=local`.
4. Run `make install`.
5. Run `make dev`.

Default local URLs:

| Service | URL |
|---------|-----|
| Frontend | `http://localhost:18000` |
| API | `http://localhost:18001` |

`make dev` starts the API from `apps/backend` and the Vite UI from
`apps/frontend`.

## Docker Compose quick start

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.

Compose runs Postgres, backend, and frontend. Auth stays inside the API image.
Leave `DATABASE_URL` blank to use the bundled database service. Override the URL
to point at another Postgres host.

## Repository layout (ops view)

| Path | Role |
|------|------|
| `apps/backend` | FastAPI convert, validate, auth, dissemination |
| `apps/frontend` | Operator UI |
| `apps/worker` | Near-realtime ingest |
| `apps/e2e` | Playwright tests |
| `packages/*` | Libraries |
| `vendor/schemas` | Read-only schema snapshots |
| `deploy/doks` | Staging and prod Kubernetes overlays |
| `config/profiles` | Conversion profile catalog for the API image |
| `config/rules` | Issue catalog and provenance map |
| `config/engineering` | Coverage surface inventories |

## Environment sync (required outcomes)

1. Keep secret names aligned across local `.env`, DOKS secrets, and CI.
2. Keep non-secret URLs and CORS lists in `deploy/profiles/` JSON.
3. Run `make env-check` after local secret edits.
4. Do not commit secrets.
5. Prefer DOKS hosts for live Auth redirect URLs. Do not re-add retired Render
 hosts.

### Secret surfaces

| Surface | Holds |
|---------|-------|
| Local `.env` | Publishable and secret Auth keys, `DATABASE_URL`, admin bootstrap |
| DOKS secrets | Same secret names for API and worker |
| GitHub Actions secrets | CI and deploy credentials only |

### Deprecated names

Do not set retired Auth key aliases after the shim window ends. See
[env-variable.md](env-variable.md) for the current name list.

## Staging and production

1. Deploy through manifests under `deploy/doks/`.
2. Keep API, frontend, and worker on the same component boundaries as
 [architecture.md](architecture.md).
3. Open feature pull requests into `stage` first when `origin/stage` exists.
4. Promote `stage` to `main` only after required CI and staging checks pass.
5. Keep `DISSEMINATION_EGRESS_ALLOWLIST` non-empty in every deployed env. An empty
 allowlist denies egress.

## Worker ops

1. Run the ingest worker as a DOKS Deployment.
2. Give the worker `DATABASE_URL` and the credentials it needs for ingest.
3. Do not configure the worker to disseminate.

## Observability

1. Keep health endpoints mounted on the API.
2. Keep Prometheus rules aligned with `deploy/doks/observability/` when present.

## Cutover and migration notes

Historical Render decommission notes and one-time database migration checklists
may remain in local `docs/ops/`. Standing truth for current ops is this contract
plus `deploy/doks/` and [env-variable.md](env-variable.md).

## Required outcomes

1. A new developer can start the local stack from the root Makefile.
2. Staging matches the architecture component map.
3. Promote follows stage-first policy.
4. Dissemination egress stays fail-closed without an allowlist.
