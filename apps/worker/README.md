# F8 Near-RT Ingest Worker

Render **Background Worker** (`apps/worker`) — ADR-018 / UJ-014.

## Pipeline

1. Poll `INGEST_POLLER_URL` (HTTPS JSON feed: `{ "items": [ { "id", "product", "tac" }, … ] }`)
2. Per job: `tac-validate` → `tac2iwxxm` → `iwxxm-validate`
3. Pass → `iwxxm_ingest_results`; fail → `iwxxm_ingest_quarantine` (service-role JWT)

## Local

```bash
uv sync --package metar-worker
export SUPABASE_URL=… SUPABASE_SERVICE_ROLE_KEY=… INGEST_POLLER_URL=…
INGEST_ONCE=1 uv run --package metar-worker python -m metar_worker
```

Tests: `make test-unit-worker`

## Deploy

Blueprint service `metar-to-iwxxm-worker` in `render.yaml` (Docker context repo root).
Apply migration `supabase/migrations/20260712000009_iwxxm_ingest_store_quarantine.sql`
before enabling the worker.
