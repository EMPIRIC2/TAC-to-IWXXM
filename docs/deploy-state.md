# Deploy State

> Last updated: 2026-07-31  
> Status: deployed (S033 / EV-026 #809 VA multi-location equality — smoke COMPLETE)

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-07-31 | 2026-07-31 | Main CI Deploy after #817 merge `101f555` |
| 2 | Smoke tests | done | 2026-07-31 | 2026-07-31 | H0c/H1/H3/H4/H5 + catalog wmoPass + VA SIGMET convert |
| 3 | Health check | done | 2026-07-31 | 2026-07-31 | `/health` 200; `tac2iwxxm_available` |
| 4 | Changelog | done | 2026-07-31 | 2026-07-31 | `docs/CHANGELOG.md` S033 entry |
| 5 | Monitoring baseline | done | 2026-07-31 | 2026-07-31 | Live SIGMET convert + FE App chunk catalog check |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR `main-latest` + Render deploy hooks |
| Commit | `101f555` (merge #817) |
| Branch | main |
| API deploy id | dep-d9miestbedkc73dr3j9g |
| FE deploy id | dep-d9mietnqj5pc73d3c8a0 |
| Images | `backend:main-latest` · `frontend:main-latest` |
| Session report | docs/sessions/S033-va-multi-location-equality/reports/deploy-smoke.md |
