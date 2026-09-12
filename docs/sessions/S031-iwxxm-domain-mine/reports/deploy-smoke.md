# Deploy smoke — S031 / EV-024 (#804 / #807 / #773 IWXXM domain mine)

> Status: **PASS**  
> Date: 2026-07-30  
> Decision: `D-S031-merge-close` — merge #813 + live smoke (T7.3 / E24-4)  
> PR: [#813](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/813) **merged**  
> Merge commit: `864783e`  
> Main CI: [30595410610](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30595410610) **success** (Deploy included)  
> API deploy: `dep-d9lvcr2jnfac73bbn340` **live**  
> FE deploy: `dep-d9lvcrrl550s73cuhvf0` **live**

## Scope

Domain mine + UJ-039 sample menu (F6 / F2 / F4 / F12 / F13 / F25 deepen): WMO reference
catalog tier, VA SIGMET stems, mining notes, validate/CI wire. Encode gaps → children
#809–#812.

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI + Deploy | `gh run 30595410610` | **PASS** |
| API Render | `dep-d9lvcr2jnfac73bbn340` live | **PASS** |
| FE Render | `dep-d9lvcrrl550s73cuhvf0` live | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| EV-024 catalog | FE `App-*.js` contains `wmoReference`, `WMO reference`, `sigmet_va_eggx`, `sigmet_multi_location_va` | **PASS** |
| EV-024 convert | Live multipart convert `metar_a3_1.tac` → IWXXM 2025-2 | **PASS** |

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# + FE App chunk catalog string check + multipart convert
```

## Health

- API healthy; EV-024 catalog UI + convert live on `…864783e` images
- FE `/config.json` points at live API
- Auth login skips expected under F21 public app

## Rollback

- Redeploy prior GHCR digests for API then FE (previous live: `dep-d9ltmt6gekts73chvs70` / `dep-d9ltmtou01pc738r8nc0`)
- Re-run `verify_connectivity.sh` + `/health` + catalog string + convert checks

## Verdict

**T7.3 / 13-deploy-smoke complete.** S031 / EV-024 IWXXM domain mine + WMO reference sample
menu live on Render; ready for Phase 4 close.
