# Deploy smoke — S033 / EV-026 (#809 VA multi-location equality)

> Status: **PASS**  
> Date: 2026-07-31  
> Decision: `D-S033-13-start` — optional 13 after #817 merge (user choice 1)  
> PR: [#817](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/817) **merged**  
> Merge commit: `101f555`  
> Main CI: [30670991313](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30670991313) **success** (Deploy included)  
> API deploy: `dep-d9miestbedkc73dr3j9g` **live**  
> FE deploy: `dep-d9mietnqj5pc73d3c8a0` **live**

## Scope

ADR-032 `canonicalize_xml` equality for WMO `sigmet-multi-location-VA` under annex3
defaults; catalog `sigmet_multi_location_va` promoted to `wmoPass`; #809 closed in Gate C.

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI + Deploy | `gh run 30670991313` | **PASS** |
| API Render | `dep-d9miestbedkc73dr3j9g` live | **PASS** |
| FE Render | `dep-d9mietnqj5pc73d3c8a0` live | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| EV-026 catalog | FE `App-BlOvxPvO.js` has `sigmet_multi_location_va`, `wmoPass:!0`, label `(passer)` | **PASS** |
| EV-026 convert | Live multipart convert + `product=SIGMET` → `VolcanicAshSIGMET` with 2018-07 / SHANWICK / EXETER / xlink / 2dp | **PASS** |
| Baseline METAR | Live convert `metar_a3_1.tac` → IWXXM 2025-2 | **PASS** |

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# + FE App chunk catalog string check + SIGMET multipart convert
```

## Health

- API healthy on post-#817 Render deploys; catalog passer + VA multi-location encode live
- FE `/config.json` points at live API; lazy `App-*.js` carries `wmoPass` catalog
- Auth login skips expected under F21 public app

## Rollback

- Redeploy prior GHCR digests for API then FE (previous live: `dep-d9mhh3tbedkc73dp5g4g` / `dep-d9mhh4jm8hqs73cc2hh0`)
- Re-run `verify_connectivity.sh` + `/health` + catalog string + SIGMET convert checks

## Verdict

**T3.4 / 13-deploy-smoke complete.** S033 / EV-026 VA multi-location ADR-032 equality +
`wmoPass` catalog live on Render; ready for Phase 4 / cycle close after user approval.
