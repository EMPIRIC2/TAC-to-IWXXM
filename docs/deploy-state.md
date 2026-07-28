# Deploy State

> Last updated: 2026-07-28  
> Status: deployed (S023 / EV-017 F21 public app validated — smoke PASS pending user sign-off)

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-07-28 | 2026-07-28 | Existing live train (#786/#787); validate-existing (no redeploy) |
| 2 | Smoke tests | done | 2026-07-28 | 2026-07-28 | H0c/H1/H3/H4/H5 + live Playwright F21/F22 5/5 |
| 3 | Health check | done | 2026-07-28 | 2026-07-28 | `/health` healthy; `/auth/login` 404; public convert 200 |
| 4 | Changelog | pending | — | — | S023 entry on cycle close |
| 5 | Monitoring baseline | done | 2026-07-28 | 2026-07-28 | H3 convert ~635ms; health ~241ms |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR `main-latest` + Render deploy hooks |
| Commit | main-latest post-#786/#787 (evolve tip docs ahead) |
| Branch | main (live) / evolve/EV-017-public-app-privacy (session) |
| API deploy id | dep-d9khddad0e5s73dmm4r0 |
| FE deploy id | dep-d9khdedbedkc73aodib0 |
| Images | `backend:main-latest` · `frontend:main-latest` (FE bake fix #787) |
| Session report | docs/sessions/S023-public-app-privacy/reports/deploy-smoke.md |
