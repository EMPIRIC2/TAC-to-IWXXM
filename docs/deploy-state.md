# Deploy State

> Last updated: 2026-08-03  
> Status: deployed (S038 / EV-031 platform independence — provisional DOKS; awaiting 13 user approval)

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-08-03 | 2026-08-03 | DOKS cutover M6; validate-existing in 13 (no new image push) |
| 2 | Smoke tests | done | 2026-08-03 | 2026-08-03 | Host-header 5/5; H0c/H4/H5; topology 3/3 |
| 3 | Health check | done | 2026-08-03 | 2026-08-03 | DOKS pods Running; Render `/health` 503 |
| 4 | Changelog | done | 2026-08-03 | 2026-08-03 | Unreleased S038 + 13 re-verify note |
| 5 | Monitoring baseline | done | 2026-08-03 | 2026-08-03 | LB 168.144.12.70 Host-header path |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-api + metar-frontend + metar-worker (DOKS `metar-iwxxm`) |
| Deploy URL (API) | `http://168.144.12.70` Host `api.doks.placeholder.metar-iwxxm.local` |
| Deploy URL (FE) | `http://168.144.12.70` Host `app.doks.placeholder.metar-iwxxm.local` |
| Deploy mode | Provisional DOKS primary (`D-S038-t63-waive`); Render suspended |
| Commit | evolve tip (see `workflow-state.yaml`) |
| Branch | `evolve/EV-031-platform-independence-842` |
| Session report | docs/sessions/S038-platform-independence-842/reports/deploy-smoke.md |
| Prior Render | Suspended — see ops/render-decommission-archive.md |
