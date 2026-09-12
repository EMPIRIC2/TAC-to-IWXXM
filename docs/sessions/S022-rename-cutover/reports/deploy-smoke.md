# Deploy Smoke — S022 / #781 rename cutover

> Date: 2026-07-27  
> Stage: 13-deploy-smoke  
> Session: S022-rename-cutover  
> Status: **PASS** (primary cutover + live UJ-032)

## Precondition (from 15)

Render primary services already retargeted and live on Empiric2 images
(`docs/sessions/S022-rename-cutover/reports/service-health.md`).

| Service | Image / repo |
|---------|----------------|
| API | `ghcr.io/empiric2/tac-to-iwxxm/backend:main-latest` |
| FE | `ghcr.io/empiric2/tac-to-iwxxm/frontend:main-latest` |
| Worker | repo `EMPIRIC2/TAC-to-IWXXM` @ `6b9d2b9` |

## Smoke matrix

| Tier | Result | Evidence |
|------|--------|----------|
| H0c | **PASS** | `make test-live-connectivity` CORS unit (6) |
| H1 | **PASS** | `GET /health` 200 healthy |
| H4 | **PASS** | Live CORS preflight (2) |
| H5 | **PASS** | `/config.json` api.baseUrl correct |
| UJ-032 | **PASS** | Live browser (auth required for Convert) |

### UJ-032 live browser

1. Opened https://metar-to-iwxxm-frontend-v4-web.onrender.com/
2. Confirmed **Examples** / `aria-label="Load golden example"` (16 catalog options)
3. Guest load of **METAR basic (annex3)** filled editor (`METAR KJFK …`) + demo banner
4. Guest Convert → auth error (expected)
5. Admin login → reload Examples → Convert → **DOWNLOAD ZIP (1)**; page contains `<?xml` / `iwxxm:METAR`

## Remaining #781 (optional / admin)

| Item | Disposition |
|------|-------------|
| PyPI Trusted Publisher → EMPIRIC2 | Still pending org admin |
| Optional Actions secrets (e2e/load) | Deferred unless those workflows required |
| Legacy joseph-repo Render services | Out of primary cutover |
| Hostname rename | Out of scope |

## Gate

| Gate | Result |
|------|--------|
| Deploy smoke (S022 primary) | **PASS** |
| Live goldens (S021 deferral) | **PASS** |
