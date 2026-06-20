# Config Spec (Monorepo Migration)

> **Ephemeral artifact** — session 01-requirements 2026-06-14  
> Env details also in docs/deploy.md and docs/api-contract.md

## Workspace

| File | Purpose |
|------|---------|
| `pyproject.toml` (root) | uv workspace members: apps/backend, packages/* |
| `pnpm-workspace.yaml` | packages: apps/frontend, apps/e2e, packages/shared |
| `vendor/manifest.json` | Pins wmo-im schema bundle versions |

## Environment Variables

### API (apps/backend)

| Name | Required | Default | Validation |
|------|----------|---------|------------|
| `SUPABASE_URL` | prod yes | — | HTTPS URL |
| `SUPABASE_ANON_KEY` | prod yes | — | non-empty |
| `METAR_CORS_ORIGINS` | prod yes | — | comma-separated origins |
| `DISABLE_AUTH` | no | `true` local | bool string |
| `FRONTEND_URL` | yes | `http://localhost:18000` | URL |
| `PORT` | Render | `8000` | int; bind 0.0.0.0 |

### Frontend (build-time)

| Name | Required | Default | Validation |
|------|----------|---------|------------|
| `VITE_API_BASE_URL` | yes | — | URL; API + auth host |
| `VITE_SUPABASE_URL` | yes | — | HTTPS URL |
| `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | yes | — | non-empty |
| `VITE_APP_URL` | yes | — | public frontend URL |

## Makefile Targets (planned)

| Target | Action |
|--------|--------|
| `install` | uv sync + pnpm install |
| `dev` | start backend + frontend |
| `test` | all workspace tests |
| `test-unit` | unit only |
| `tests:e2e` | Playwright apps/e2e |
| `vendor-sync` | run scripts/vendor/sync-iwxxm.sh |

## CLI Flags

No new CLI — existing Makefile and docker compose remain entry points.
