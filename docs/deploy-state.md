# Deploy State

> Last updated: 2026-07-30  
> Status: deployed (S027 / EV-021 F26 VAA + F27 TCA — smoke COMPLETE)

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-07-30 | 2026-07-30 | Main CI Deploy after #794 merge `df56d1f` |
| 2 | Smoke tests | done | 2026-07-30 | 2026-07-30 | H0c/H1/H3/H4/H5 + live VAA/TCA catalog/lint/convert |
| 3 | Health check | done | 2026-07-30 | 2026-07-30 | `/health` 200; `tac2iwxxm_available` |
| 4 | Changelog | done | 2026-07-30 | 2026-07-30 | `docs/CHANGELOG.md` S027 entry |
| 5 | Monitoring baseline | done | 2026-07-30 | 2026-07-30 | Convert VAA/TCA multipart smoke <2s |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR `main-latest` + Render deploy hooks |
| Commit | `df56d1f` (merge #794) |
| Branch | main |
| API deploy id | dep-d9lmsdflk1mc739232ug |
| FE deploy id | dep-d9lmsefqj5pc739d3it0 |
| Images | `backend:main-latest` · `frontend:main-latest` |
| Session report | docs/sessions/S027-vaa-quality/reports/deploy-smoke.md |
