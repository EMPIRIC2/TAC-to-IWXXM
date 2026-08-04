# Deploy report — S038 / EV-031 (stub)

> **Status**: provisional DOKS cutover (day 0+ soak) — **not** final production DNS  
> **Decision**: `D-S038-t63-waive`  
> **Date**: 2026-08-03

## Topology

| Layer | Target |
|-------|--------|
| Compute | DOKS namespace `metar-iwxxm` |
| LB | `168.144.12.70` |
| API Host | `api.doks.placeholder.metar-iwxxm.local` |
| FE Host | `app.doks.placeholder.metar-iwxxm.local` |
| Product DB | DigitalOcean Postgres (`DATABASE_URL`) |
| Auth | Supabase Auth (JWKS-only) |

Public `config/prod.json` `api.baseUrl` remains Render until real DNS.

## Smoke evidence

| Check | Command | Result |
|-------|---------|--------|
| Host-header cutover | `bash scripts/deploy/doks_host_header_smoke.sh` | PASS (T6.4) |
| H4–H5 | `make test-live-connectivity-doks-provisional` | PASS (T7.2) |
| Playwright F31 | `make test-live-e2e-doks-provisional` | 13/13 (T7.1) |
| TC-EV031 topology | `make test-live-topology-doks-provisional` | 3/3 (T7.3) |

## Interim ops

- API: ConfigMap mount for `sslmode=require` work-sessions fix (pending GHCR republish)
- FE: hot-copied F31 `dist` into running pod (pending `frontend:ev031-doks` push)

## Follow-up

- Complete soak → **T6.5** Render decommission checklist
- Pin real DNS; update Ingress / `LIVE_*` / public `api.baseUrl`
- Finalize this report at cycle close / 13-deploy-smoke
