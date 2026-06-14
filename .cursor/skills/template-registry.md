# Template Registry — METAR to IWXXM Backend

Central reference for project templates. Pipeline stages (00–19) use this file when choosing
deployment patterns, CI parity, and integration conventions.

## Service archetypes

| Archetype | When to use | Stack hints |
|-----------|-------------|-------------|
| `api` | HTTP API with DB | FastAPI + Postgres + Docker |
| `worker` | Async jobs | Background worker + queue (if needed) |
| `static+api` | Browser UI + API | Frontend static host + API service |

This backend is **`api`** (FastAPI). Frontend lives in monorepo `frontend/` submodule.

## CI parity

| Check | Command (local) | Workflow |
|-------|-----------------|----------|
| Lint | `uv run ruff check src tests` | `ci-cd.yml` backend job |
| Test | `uv run pytest tests` | `ci-cd.yml` backend job |
| Typecheck | Add when adopted | — |

Monorepo workflows live at repo root: `.github/workflows/ci-cd.yml`.

## Deploy target

| Field | Value |
|-------|-------|
| Platform | docker (Compose locally; Render images in CI) |
| Health | `GET /health` or project equivalent |
| Migrations | Document in `docs/deploy.md` |

## Customization

1. Fill `docs/spec.md` and `docs/deploy.md` during 04-tech-plan
2. Add ADR in `docs/adr/` when deviating from defaults
3. Update this registry when template choice changes
