# Deploy State

> Last updated: 2026-07-19  
> Status: deployed

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-07-19T23:03Z | 2026-07-19T23:10Z | CI Deploy `29707270877`; hooks → API + FE live |
| 2 | Smoke tests | done | 2026-07-19T23:11Z | 2026-07-19T23:12Z | H0c/H1/H3/H4/H5 + H6′ UJ-022 PASS |
| 3 | Health check | done | 2026-07-19T23:11Z | 2026-07-19T23:12Z | `/health` healthy; tac2iwxxm_available |
| 4 | Changelog | done | 2026-07-19 | 2026-07-19 | `docs/CHANGELOG.md` S014 entry |
| 5 | Monitoring baseline | done | 2026-07-19 | 2026-07-19 | H3 response-times acceptable; no crash loops |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR `main-latest` + Render deploy hooks |
| Commit | c73e0ad (merge #726) |
| Branch | main |
| API deploy id | dep-d9elikt7vvec739dpf7g |
| FE deploy id | dep-d9elilbtqb8s73ao52hg |
| Session report | docs/sessions/S014-package-publish-validation/reports/deploy-smoke.md |
