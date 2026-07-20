# Deploy State

> Last updated: 2026-07-20  
> Status: deployed

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-07-20T18:09Z | 2026-07-20T18:11Z | CI Deploy `29766213356`; hooks → API + FE live @ `37be5f8` |
| 2 | Smoke tests | done | 2026-07-20T18:12Z | 2026-07-20T18:18Z | H0c/H3/H4/H5 + AHL + COLLECT 501 + live workbench PASS |
| 3 | Health check | done | 2026-07-20T18:12Z | 2026-07-20T18:12Z | `/health` healthy; convert-bulletin OK |
| 4 | Changelog | done | 2026-07-20 | 2026-07-20 | `docs/CHANGELOG.md` S016 entry |
| 5 | Monitoring baseline | done | 2026-07-20T18:12Z | 2026-07-20T18:18Z | H3 response-times acceptable |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR `main-latest` + Render deploy hooks |
| Commit | 37be5f8 (merge #746) |
| Branch | main |
| API deploy id | dep-d9f69f3bc2fs7397bqig |
| FE deploy id | dep-d9f69fjbc2fs7397brq0 |
| Session report | docs/sessions/S016-manual-tac-input-modes/reports/deploy-smoke.md |
