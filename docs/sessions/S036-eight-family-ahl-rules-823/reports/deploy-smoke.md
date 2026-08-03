# Deploy smoke — S036 / EV-029 (T12.6 / 13)

> Status: **PASS** (awaiting user close approval)  
> Date: 2026-08-02  
> Decision: **D-S036-13-merge** = 1 (merge #828 + live smoke)  
> PR: [#828](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/828) **merged**  
> Merge commit: `4e6577a`  
> Main CI: [30773122547](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30773122547) **success** (Deploy included)  
> API deploy: `dep-d9ntlclbedkc73fvcuvg` **live** (image tag `20260802235621-4e6577a`)  
> FE deploy: `dep-d9ntlde1egvs738ph9h0` **live** (image tag `20260802235621-4e6577a`)  
> Note: Render reports platform image digests that differ from buildx index digests; FE App chunk verified for SWXA Examples.

## Scope

API + FE: eight-family AHL/`reportStatus` deepen + **F28** SWXA quality bar
(`product=swxa`) + Examples unlock `spacewx-A7-3` (TC-EV029-008 / TC-F28-005).

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI + Deploy | `gh run 30773122547` | **PASS** |
| API Render | `dep-d9ntlclbedkc73fvcuvg` live | **PASS** |
| FE Render | `dep-d9ntlde1egvs738ph9h0` live | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| F28 catalog | `GET /lint-issue-catalog?product=swxa` (≥1; `MISSING_SWXC`) | **PASS** (5) |
| F28 lint+convert | Live multipart `swxa_a7_3` → `iwxxm:SpaceWeatherAdvisory` | **PASS** |
| TC-EV029-008 FE | App chunk contains `swxa_a7_3` / `spacewx-A7-3` | **PASS** |

### Live commands

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# Catalog + product smoke:
# GET /api/v1/lint-issue-catalog?product=swxa
# POST /api/v1/lint-tac + /convert (manual_text, product=swxa, profile=annex3)
```

## Health

- API healthy; SWXA convert live on `…4e6577a` image
- FE `/config.json` points at live API; lazy `App-*.js` includes SWXA Example seed
- Auth login skips expected under F21 public app

## Rollback

- Pin prior GHCR tags (e.g. `frontend:20260802142337-c338108` / matching backend) via Render
  `PATCH` `image: { ownerId, registryCredentialId, imagePath }` then redeploy
- Re-run `verify_connectivity.sh` + `/health` + SWXA catalog/convert

## Verdict

**T12.6 / 13-deploy-smoke complete (technical).** F28 SWXA + eight-family AHL deepen live on
Render with H1–H5 green. Remaining: user approve smoke → T12.7 close (#823 / evolve summary).
