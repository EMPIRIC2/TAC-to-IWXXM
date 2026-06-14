<!-- TEMPLATE: deployment-integration.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# Deployment Integration Plan

> **Project**: deployed service — [short description]
> **Repository**: [Repository URL]
> **Last updated**: [Date]

## Overview

How the RAG API, data-management layer, and database are deployed and wired together.

### Deployment Goals

| Goal | Description | Priority |
|------|-------------|----------|
| [e.g., Reliable query API] | [HTTP availability, p95 latency target] | High |
| [e.g., Schema migrations] | [Zero-downtime or maintenance-window strategy] | High |
| [e.g., Worker ingest] | [Async indexing separate from API] | Medium |

## Runtime Architecture

### Services

| Service | Role | Image / runtime | Replicas | Health |
|---------|------|-----------------|----------|--------|
| [api] | Query + admin HTTP | [Docker / Render web] | [N] | `GET /health` |
| [worker] | Ingest / embed / index | [worker process] | [N] | [queue depth / heartbeat] |
| [postgres] | Primary + pgvector | [managed Postgres] | [1] | connection pool |

### Network & URLs

| Environment | API base URL | Notes |
|-------------|--------------|-------|
| local | `http://localhost:8000` | Docker Compose |
| staging | [URL] | Migrations on deploy |
| production | [URL] | Secrets from platform |

## Database Integration

### Connection

- **Driver**: [asyncpg / psycopg / SQLAlchemy URL]
- **Pool size**: [min/max]
- **SSL**: [required mode]

### Schema ownership

| Area | Tables (examples) | Owner module |
|------|-------------------|--------------|
| Corpus | `documents`, `chunks`, `embeddings` | `src/db/` |
| Jobs | `ingestion_jobs`, `job_events` | `src/db/` |
| RAG config | `collections`, `settings` | `src/db/` |

### Migrations

- **Tool**: [Alembic]
- **Run when**: [deploy hook / init container / manual gate]
- **Rollback**: [strategy]

## Vector store

| Choice | Details |
|--------|---------|
| [pgvector / external] | [dimension, index type (HNSW/IVFFlat), distance metric] |

## Secrets & configuration

| Secret | Platform name | Used by |
|--------|---------------|---------|
| `DATABASE_URL` | [render secret] | API, worker |
| `OPENAI_API_KEY` | [...] | embed + generate |
| [...] | [...] | [...] |

## CI/CD

| Trigger | Steps |
|---------|-------|
| PR | lint, typecheck, unit + integration tests (ephemeral DB) |
| merge to main | build image, migrate staging, deploy, smoke H1–H3 + **H4–H5** (`verify_connectivity.sh`) |

## Browser connectivity (static UI + separate APIs)

Document per `.cursor/skills/connectivity-gates.md`:

- **Build-time:** `VITE_*` on each frontend (DO BUILD_TIME secrets); redeploy frontend after URL change
- **Run-time:** `METAR_CORS_ORIGINS` on each browser-facing API (comma-separated frontend origins)
- **Staging env:** `METAR_STAGING_*_FRONTEND_URL` for H4–H5 gates

Without CORS or a same-origin BFF, production UI will show “Failed to fetch” while `curl` smokes pass.

## Observability

| Signal | Tool | Alert threshold |
|--------|------|-----------------|
| API errors | [logs/metrics] | [5xx rate] |
| Query latency | [APM] | [p95 ms] |
| Ingest backlog | [queue depth / job table] | [N pending] |
| DB connections | [pool metrics] | [max %] |

## Rollback

1. [Revert deploy artifact]
2. [Forward-only migrations vs down migration policy]
3. [Disable worker consumers]

## Open decisions

- [ ] [Embedding provider]
- [ ] [Split API vs worker deploy]
