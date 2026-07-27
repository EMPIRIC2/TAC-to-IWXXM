# Deploy State

> Last updated: 2026-07-27  
> Status: deployed (FE tip still pre–F7.g; EV-016 live smoke waived → #781)

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-07-22T23:53Z | 2026-07-23T00:00Z | CI Deploy `29967487455`; hooks → API + FE live @ `eae8bdc` |
| 2 | Smoke tests | done | 2026-07-23T00:02Z | 2026-07-23T00:03Z | H0c/H1/H3/H4/H5 + catalog taf/speci + lint/convert PASS |
| 3 | Health check | done | 2026-07-23T00:02Z | 2026-07-23T00:02Z | `/health` healthy; `tac2iwxxm_available` |
| 4 | Changelog | done | 2026-07-22 | 2026-07-22 | `docs/CHANGELOG.md` S020 entry |
| 5 | Monitoring baseline | done | 2026-07-23T00:02Z | 2026-07-23T00:03Z | H3 response-times acceptable |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR `main-latest` + Render deploy hooks |
| Commit | eae8bdc (merge #778) |
| Branch | main |
| API deploy id | dep-d9gljeupbkes73bspkl0 |
| FE deploy id | dep-d9gljfrbc2fs738q90d0 |
| Images | `backend:20260722235831-eae8bdc` · `frontend:20260722235831-eae8bdc` |
| Session report | docs/sessions/S020-aerodrome-quality/reports/deploy-smoke.md |
