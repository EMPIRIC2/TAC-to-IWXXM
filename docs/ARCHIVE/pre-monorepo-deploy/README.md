# Pre-Monorepo Deployment Docs (Archived)

These documents describe the **legacy three-service layout** (separate auth web service,
`ALLOWED_ORIGINS`, `VITE_AUTH_SERVICE_URL` / `VITE_BACKEND_URL`, Loki/Prometheus/Grafana
observability stack, and git submodules). They were archived during monorepo migration task
T11.3 (2026-06-20).

## Successor documentation

| Topic | Current doc |
|-------|-------------|
| Deployment topology & env vars | [docs/deploy.md](../../deploy.md) |
| Staging Render values | [docs/ops/staging-secrets-matrix.md](../../ops/staging-secrets-matrix.md) |
| Local development | [docs/ops/DEVELOPMENT.md](../../ops/DEVELOPMENT.md) |
| Auth merged into API | [docs/adr/ADR-002-auth-merged-into-backend.md](../../adr/ADR-002-auth-merged-into-backend.md) |
| API endpoints | [docs/api-contract.md](../../api-contract.md) |

## Archived files

- `RENDER_DEPLOYMENT.md` — three-service Render blueprint guide
- `RENDER_DEPLOYMENT_INDEX.md` — index for legacy Render docs
- `RENDER_CHECKLIST.md` — pre-migration deploy checklist
- `RENDER_VERIFICATION.md` — post-deploy verification (3-service)
- `RENDER_OBSERVABILITY.md` — Loki/Prometheus/Grafana setup (removed per ADR-006)
- `RENDER_GHCR_EXECUTABLE_CHECKLIST.md` — GHCR image workflow (superseded)
- `ENVIRONMENT_VARIABLES.md` — env reference with auth service vars
- `AUTH_MIDDLEWARE_ARCHITECTURE.md` — separate auth proxy architecture (superseded by M4)
- `SETUP_DOCKER.md` — three-service Docker Compose guide
