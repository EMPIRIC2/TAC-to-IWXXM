# Deploy smoke — S027 / EV-021 (F26 / F27 / #736 / #737)

> Status: **PASS**  
> Date: 2026-07-30  
> Decision: **D-S027-E21-13-merge** (merge #794 + live smoke + close path)  
> PR: [#794](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/794) **merged**  
> Merge commit: `df56d1f`  
> Main CI: [30556489827](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30556489827) **success** (Deploy included)  
> WMO quality: [30556489771](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30556489771) **success**  
> API deploy: `dep-d9lmsdflk1mc739232ug` **live**  
> FE deploy: `dep-d9lmsefqj5pc739d3it0` **live**

## Scope

API + FE: VAA quality bar (F26) + TCA quality bar (F27) + Examples WMO-passers unlock
(F7.g deepen) + registry deepen (F12) + convert fidelity (F6.f).

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI + Deploy | `gh run 30556489827` | **PASS** |
| WMO quality pack | `gh run 30556489771` | **PASS** |
| API Render | `dep-d9lmsdflk1mc739232ug` live | **PASS** |
| FE Render | `dep-d9lmsefqj5pc739d3it0` live | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| F26/F27 catalog | `GET /lint-issue-catalog` vaa=8 tca=7 | **PASS** |
| F26/F27 lint+convert | Live multipart `vaa_a7_2` / `tca_a2_2` → `iwxxm:VolcanicAshAdvisory` / `iwxxm:TropicalCycloneAdvisory` | **PASS** |

### Live F26/F27 smoke (TC-F26-005 / TC-F27-005)

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# Catalog + product smoke (multipart; keep multi-line VAA/TCA TAC whole):
# GET /api/v1/lint-issue-catalog?product=vaa|tca
# POST /api/v1/lint-tac + /convert for annex3_golden vaa_a7_2 / tca_a2_2
```

## Health

- API healthy; VAA + TCA convert live on `…df56d1f` image
- FE `/config.json` points at live API
- Auth login skips expected under F21 public app

## Rollback

- Redeploy prior GHCR digests for API then FE (`dep-d9l5rfid0e5s73erlkm0` / `dep-d9l5rgm417fc73d6v7gg`)
- Re-run `verify_connectivity.sh` + `/health` + catalog GET `product=vaa|tca`

## Verdict

**T6.5 / 13-deploy-smoke complete.** F26 VAA + F27 TCA quality bars live on Render; M6 / Phase D ready to close.
