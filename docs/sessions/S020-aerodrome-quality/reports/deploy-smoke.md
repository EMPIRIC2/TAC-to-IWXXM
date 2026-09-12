# Deploy smoke — S020 / EV-015 (F20)

> Date: 2026-07-22  
> Status: **deployed** — T5.7 PASS  
> PR: [#778](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/778) (merged `eae8bdc`)  
> Main tip: `eae8bdc` → CI/CD run `29967487455` Deploy **SUCCESS**  
> API: https://metar-to-iwxxm-api.onrender.com (`dep-d9gljeupbkes73bspkl0` live)  
> Frontend: https://metar-to-iwxxm-frontend-v4-web.onrender.com (`dep-d9gljfrbc2fs738q90d0` live)  
> Images: `ghcr.io/.../backend:20260722235831-eae8bdc` · `frontend:20260722235831-eae8bdc`

## Pre-deploy

| Check | Result |
|-------|--------|
| 11-verify-impl | PASS (`D-S020-EV015-11-A`); H4–H5 deferred to T5.7 |
| Merge approval | User `D-S020-EV015-merge-778` — merge now + live smoke + close M5/Phase D |
| PR #778 CI (pre-merge tip `c5fb752`) | All required checks SUCCESS |
| Merge → main | `eae8bdcfea86351f7755c8e54750ac14a33130b1` |
| GHCR + Render deploy hooks | CI Deploy job success; API + FE `live` on `…-eae8bdc` |

## Smoke results

| Tier | What | Result |
|------|------|--------|
| H0ci | CI/CD on `main` @ `eae8bdc` (incl. Deploy) | **PASS** |
| H1 | API `/health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS policy unit tests | **PASS** 6/6 |
| H3 | `make test-live-api` | **PASS** 21/21 |
| H4 | Live CORS preflight (FE origin + work-sessions PATCH) | **PASS** 2/2 |
| H5 | Frontend `/config.json` `api.baseUrl` → API | **PASS** |
| F20 catalog | Auth → `GET /api/v1/lint-issue-catalog?product=taf` (24; has `MISSING_VALIDITY`); `product=speci` (32; has `MISSING_CCCC`) | **PASS** |
| F20 lint+convert | Live `POST /lint-tac` + `/convert` for TAF + SPECI accept fixtures | **PASS** |

Commands:

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# Catalog + product smoke: login → GET catalog?product=taf|speci → lint-tac/convert
```

## Health

- API healthy; convert/auth paths green in H3
- TAF/SPECI catalog filters live on image `…-eae8bdc`
- FE `config.json` points at production API

## Rollback

- Redeploy prior GHCR digest (`…-365c068`) for API then frontend
- Re-run `verify_connectivity.sh` + `/health` + catalog GET taf/speci
- No DB migrations this cycle — image-only rollback

## Verdict

**T5.7 / 13-deploy-smoke complete.** F20 TAF+SPECI quality bar live on Render; M5 / Phase D ready to close.
