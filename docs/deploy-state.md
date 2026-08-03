# Deploy State

> Last updated: 2026-08-02  
> Status: deployed (S036 / EV-029 #823 eight-family AHL + F28 SWXA — smoke PASS)

## Deployment Log

| # | Step | Status | Started | Completed | Notes |
|---|------|--------|---------|-----------|-------|
| 1 | Deploy | done | 2026-08-02 | 2026-08-02 | Main CI Deploy after #828 merge `4e6577a` |
| 2 | Smoke tests | done | 2026-08-02 | 2026-08-02 | H0c/H1/H3/H4/H5 + SWXA catalog/convert + FE App chunk |
| 3 | Health check | done | 2026-08-02 | 2026-08-02 | `/health` 200; `tac2iwxxm_available` |
| 4 | Changelog | pending | — | — | Append after user smoke approval |
| 5 | Monitoring baseline | done | 2026-08-02 | 2026-08-02 | Live SWXA convert + FE Examples seed check |

## Current Deployment

| Field | Value |
|-------|-------|
| App name | metar-to-iwxxm-api + metar-to-iwxxm-frontend-v4-web |
| Deploy URL (API) | https://metar-to-iwxxm-api.onrender.com |
| Deploy URL (FE) | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Deploy mode | GHCR immutable tag then restore `main-latest` |
| Commit | `4e6577a` (merge #828) |
| Branch | main |
| API deploy id | dep-d9ntlclbedkc73fvcuvg |
| FE deploy id | dep-d9ntlde1egvs738ph9h0 |
| Images | `backend:20260802235621-4e6577a` · `frontend:20260802235621-4e6577a` (service imagePath restored to `main-latest`) |
| Session report | docs/sessions/S036-eight-family-ahl-rules-823/reports/deploy-smoke.md |
