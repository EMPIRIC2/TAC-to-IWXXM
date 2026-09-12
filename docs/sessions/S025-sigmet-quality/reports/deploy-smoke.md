# Deploy smoke — S025 / EV-019 (F23 / #733+#739)

> Status: **PASS**  
> Date: 2026-07-29  
> Decision: **D-S025-13-deploy-A** (merge now + live smoke + close)  
> PR: [#792](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/792) **merged**  
> Merge commit: `afffe86`  
> Main CI: [30461326056](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30461326056) **success** (Deploy included)  
> API deploy: `dep-d9l11761egvs738ho3r0` **live**  
> FE deploy: `dep-d9l1187avr4c739rfl10` **live**

## Scope

API + FE: SIGMET/VA lint+convert quality bar + FE catalog SIGMET/VA tags (E19-17).

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI + Deploy | `gh run 30461326056` | **PASS** |
| API Render | `dep-d9l11761egvs738ho3r0` live | **PASS** |
| FE Render | `dep-d9l1187avr4c739rfl10` live | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| F23 catalog | `GET /lint-issue-catalog?product=sigmet` (26; `SIGMET_CNL` + `NO_VA_EXP`) | **PASS** |
| F23 lint+convert | Live multipart `lint-tac` + `convert` general → `SIGMET`; VA → `VolcanicAshSIGMET` | **PASS** |

### Live F23 smoke (TC-F23-005)

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# Catalog + product smoke (multipart):
# GET /api/v1/lint-issue-catalog?product=sigmet
# POST /api/v1/lint-tac + /convert product=SIGMET (general + VA fixtures)
```

## Health

- API healthy; SIGMET convert roots live on `…afffe86` image
- FE catalog preferred tags include `sigmet` / `va`
- Auth login skips expected under F21 public app

## Rollback

- Redeploy prior GHCR digests for API then FE (`dep-d9kkpfijobas73fp404g` / prior FE)
- Re-run `verify_connectivity.sh` + `/health` + catalog GET `product=sigmet`

## Verdict

**T5.6 / 13-deploy-smoke complete.** F23 SIGMET + VA quality bar live on Render; M5 / Phase D ready to close.
