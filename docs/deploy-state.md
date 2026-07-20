# Deploy State

> Last updated: 2026-07-20  
> Status: deployed

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-07-20T05:16Z | 2026-07-20T05:22Z | CI Deploy `29718764520`; hooks → API + FE live @ `b405a96` |
| 2 | Smoke tests | done | 2026-07-20T05:23Z | 2026-07-20T05:24Z | H0c/H1/H3/H4/H5 + F15 catalog PASS |
| 3 | Health check | done | 2026-07-20T05:23Z | 2026-07-20T05:23Z | `/health` healthy; tac2iwxxm_available |
| 4 | Changelog | pending | — | — | S015 entry at evolve close |
| 5 | Monitoring baseline | done | 2026-07-20T05:23Z | 2026-07-20T05:24Z | H3 response-times acceptable |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR `main-latest` + Render deploy hooks |
| Commit | b405a96 (merge #742) |
| Branch | main |
| API deploy id | dep-d9er13v7f7vs73b8deug |
| FE deploy id | dep-d9er14f41pts73feb650 |
| Session report | docs/sessions/S015-metar-lint-quality/reports/deploy-smoke.md |
