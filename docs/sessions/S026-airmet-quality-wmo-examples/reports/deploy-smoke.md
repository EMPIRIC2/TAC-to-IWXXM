# Deploy smoke — S026 / EV-020 (F24 / F25 / #731)

> Status: **PASS**  
> Date: 2026-07-29  
> Decision: **D-S026-E20-13-merge** (merge #793 + live smoke + close path)  
> PR: [#793](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/793) **merged**  
> Merge commit: `0f77194`  
> Main CI: [30485625474](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30485625474) **success** (Deploy included)  
> WMO quality: [30485625688](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30485625688) **success**  
> API deploy: `dep-d9l5ihf10e5c73fs5420` **live**  
> FE deploy: `dep-d9l5ii9t0dsc73fr60gg` **live**

## Scope

API + FE: AIRMET quality bar (F24) + WMO METAR/SPECI/TAF golden parity + Examples WMO-passers gate (F25) + decode glossary deepen (F9).

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI + Deploy | `gh run 30485625474` | **PASS** |
| WMO quality pack | `gh run 30485625688` | **PASS** |
| API Render | `dep-d9l5ihf10e5c73fs5420` live | **PASS** |
| FE Render | `dep-d9l5ii9t0dsc73fr60gg` live | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| F24/F25 catalog | `GET /lint-issue-catalog` airmet=11 metar=32 taf=24 sigmet=26 | **PASS** |
| F24/F25 lint+convert+decode | Live multipart AIRMET + METAR/SPECI/TAF WMO fixtures → correct `iwxxm:*` roots | **PASS** |

### Live F24/F25 smoke (TC-F24-005 / TC-F25-004)

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# Catalog + product smoke (multipart, whitespace-normalized TAC):
# GET /api/v1/lint-issue-catalog?product=airmet|metar|taf|sigmet
# POST /api/v1/lint-tac + /convert + /decode-tac for annex3_golden WMO fixtures
```

Note: multiline AIRMET vendor TAC must be whitespace-normalized before multipart convert
(live splitter treats physical newlines as bulletin boundaries).

## Health

- API healthy; AIRMET + WMO METAR/SPECI/TAF convert live on `…0f77194` image
- FE `/config.json` points at live API
- Auth login skips expected under F21 public app

## Rollback

- Redeploy prior GHCR digests for API then FE (`dep-d9l17e5f1gfc73dcuo50` / `dep-d9l17f0ae00c7388ephg`)
- Re-run `verify_connectivity.sh` + `/health` + catalog GET `product=airmet`

## Verdict

**T6.5 / 13-deploy-smoke complete.** F24 AIRMET + F25 WMO goldens live on Render; M6 / Phase D ready to close.
