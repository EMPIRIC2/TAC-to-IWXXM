# F8 Near-RT Ingest Worker

Render **Background Worker** (`apps/worker`) — ADR-018 (amended ADR-033 / F30) / UJ-014.

## Pipeline

1. Poll `INGEST_POLLER_URL` (HTTPS JSON feed: `{ "items": [ { "id", "product", "tac" }, … ] }`)
2. Per job: `tac-validate` → `tac2iwxxm` → `iwxxm-validate`
3. Pass → `iwxxm_ingest_results`; fail → `iwxxm_ingest_quarantine` via **`DATABASE_URL`**
   (DigitalOcean Postgres / SQLAlchemy — not Supabase PostgREST)

## Local

```bash
uv sync --package metar-worker
export DATABASE_URL=… INGEST_POLLER_URL=…
# Apply product schema once (same Alembic tree as API):
make db-migrate
INGEST_ONCE=1 uv run --package metar-worker python -m metar_worker
```

Tests: `make test-unit-worker`

## Deploy

Blueprint service `metar-to-iwxxm-worker` in `render.yaml` (Docker context repo root).
Required secrets: `DATABASE_URL`, `INGEST_POLLER_URL`. Product schema from
`apps/backend` Alembic (`make db-migrate` / CI `alembic upgrade head`).
