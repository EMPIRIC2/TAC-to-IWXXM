# Deploy State

> Last updated: 2026-07-28  
> Status: deployed (S023 / EV-017 F21 public app — smoke COMPLETE)

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-07-28 | 2026-07-28 | Validate-existing; then API env cleanup redeploy `dep-d9kii12jobas73fl4bi0` |
| 2 | Smoke tests | done | 2026-07-28 | 2026-07-28 | H0c/H1/H3/H4/H5 + Playwright F21/F22 5/5; post-cleanup re-PASS |
| 3 | Health check | done | 2026-07-28 | 2026-07-28 | `/health` 200; `/auth/login` 404; public convert 200 |
| 4 | Changelog | done | 2026-07-28 | 2026-07-28 | `docs/CHANGELOG.md` S023 entry |
| 5 | Monitoring baseline | done | 2026-07-28 | 2026-07-28 | Convert ~635ms; health ~241ms |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR `main-latest` + Render deploy hooks |
| Commit | main-latest post-#786/#787 |
| Branch | main (live) / evolve/EV-017-public-app-privacy (session) |
| API deploy id | dep-d9kii12jobas73fl4bi0 |
| FE deploy id | dep-d9khdedbedkc73aodib0 |
| Images | `backend:main-latest` · `frontend:main-latest` |
| Session report | docs/sessions/S023-public-app-privacy/reports/deploy-smoke.md |
| API Auth leftovers | `SUPABASE_URL` / `SUPABASE_SECRET_KEY` **removed** (worker keys retained) |
