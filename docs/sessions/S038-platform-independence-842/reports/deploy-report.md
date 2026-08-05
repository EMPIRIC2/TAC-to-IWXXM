# Deploy report — S038 / EV-031

> **Status**: DOKS primary **validated** (13-deploy-smoke); Render **suspended** — **not** final production DNS  
> **Decisions**: `D-S038-t63-waive` (DNS) · `D-S038-t65-waive` (soak / decommission) · `D-S038-12` = 1  
> **Date**: 2026-08-03  
> **13 report**: [deploy-smoke.md](deploy-smoke.md)

## Topology

| Layer | Target |
|-------|--------|
| Compute | DOKS namespace `metar-iwxxm` (**primary**) |
| LB | `168.144.12.70` |
| API Host | `api.doks.placeholder.metar-iwxxm.local` |
| FE Host | `app.doks.placeholder.metar-iwxxm.local` |
| Product DB | DigitalOcean Postgres (`DATABASE_URL`) |
| Auth | Supabase Auth (JWKS-only) |
| Render | Suspended — [ops/render-decommission-archive.md](../../../ops/render-decommission-archive.md) |

`config/prod.json` `api.baseUrl` / `frontendUrl` / `liveE2e.*` → provisional DOKS placeholders.

## Smoke evidence

| Check | Command | Result |
|-------|---------|--------|
| Host-header cutover | `bash scripts/deploy/doks_host_header_smoke.sh` | **5/5 PASS** (T6.4 + 13 re-verify) |
| H4–H5 | `make test-live-connectivity-doks-provisional` | **PASS** (T7.2 + 13 re-verify) |
| Playwright F31 | `make test-live-e2e-doks-provisional` | 13/13 (T7.1) |
| TC-EV031 topology | `make test-live-topology-doks-provisional` | **3/3 PASS** (T7.3 + 13 re-verify) |
| Render suspend | API `/health` after T6.5 / 13 | **503** (expected) |
| DOKS pods | `kubectl -n metar-iwxxm get pods` | API+FE+worker Running |

## Interim ops

- API: ConfigMap mount for `sslmode=require` work-sessions fix (pending GHCR republish)
- FE: hot-copied F31 `dist` into running pod (pending `frontend:ev031-doks` push)
- CI Deploy: GHCR push only; Render hooks retired

## Follow-up

- Pin real DNS; update Ingress / public HTTPS URLs; lift `D-S038-t63-waive`
- Republish GHCR images; remove interim ConfigMap / hot-copy
- Evolve PR → `main` after user approves 13 + Phase D close
