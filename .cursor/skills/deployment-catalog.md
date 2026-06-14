# Deployment Catalog — METAR to IWXXM Backend

Quick reference for deployment options documented during 04-tech-plan. Pick one primary path;
record the choice in `workflow-state.yaml` §`deployment`.

## Platform options

| Option | Fit | Notes |
|--------|-----|-------|
| **Docker Compose** | Local + integration | Monorepo `docker-compose.yml` |
| **Render** | Staging/production | CI builds images to GHCR |
| **K8s** | If org standard | Not default unless required |

## Data store

| Option | Fit |
|--------|-----|
| **Postgres** | Primary — async SQLAlchemy + asyncpg |
| SQLite | Local dev only if documented |

## Cross-service (monorepo)

| Service | Role |
|---------|------|
| `backend` | METAR/IWXXM API (this repo path) |
| `auth` | Authentication service |
| `frontend` | React UI (submodule) |

Detail: [connectivity-gates.md](connectivity-gates.md) and `docs/deploy.md` §Integration.

## Secrets

- Never commit `.env` with real credentials
- Use platform secret stores (Render, Compose env files locally)
- Prefix pattern: `{{CONFIG_PREFIX}}_*` — fill during 04-tech-plan
