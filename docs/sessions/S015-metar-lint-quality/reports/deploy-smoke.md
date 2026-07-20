# Deploy smoke — S015 / EV-011 (F15)

> Date: 2026-07-20  
> Status: **deployed** — T5.10 PASS  
> PR: [#742](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/742) (merged `b405a96`)  
> Main tip: `b405a96` → CI/CD run `29718764520` Deploy **SUCCESS**  
> API: https://metar-to-iwxxm-api.onrender.com (`dep-d9er13v7f7vs73b8deug` live 2026-07-20T05:22:55Z)  
> Frontend: https://metar-to-iwxxm-frontend-v4-web.onrender.com (`dep-d9er14f41pts73feb650` live 2026-07-20T05:22:38Z)  
> Images: `ghcr.io/.../backend:20260720052043-b405a96` · `frontend:20260720052043-b405a96`

## Pre-deploy

| Check | Result |
|-------|--------|
| 12-verify-deploy checklist | READY (T5.9) |
| Merge approval | User continue → merge #742 |
| PR #742 CI (pre-merge tip `2b4ec29`) | All required checks SUCCESS |
| Merge → main | `b405a96` |
| GHCR + Render deploy hooks | CI Deploy job success; API + FE `live` |

## Smoke results

| Tier | What | Result |
|------|------|--------|
| H0ci | CI/CD on `main` @ `b405a96` (incl. Deploy) | **PASS** |
| H1 | API `/health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS policy unit tests | **PASS** 6/6 |
| H3 | `make test-live-api` | **PASS** 21/21 |
| H4 | Live CORS preflight (FE origin + work-sessions PATCH) | **PASS** 2/2 |
| H5 | Frontend `/config.json` `api.baseUrl` → API | **PASS** |
| F15 catalog | `GET /api/v1/lint-issue-catalog` unauth 401; auth → 35 issues | **PASS** |
| F15 CORS | `OPTIONS` catalog → `Access-Control-Allow-Origin` FE | **PASS** |

Commands:

```bash
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
# Catalog: POST /auth/login → GET /api/v1/lint-issue-catalog
```

## Health

- API healthy; convert/auth paths green in H3
- Catalog route live on image `…-b405a96` (35 registry issues)
- FE `config.json` points at production API

## PyPI (E11-25)

- Planned tag: `tac-validate-v0.1.1` — **not cut in T5.10** (await Phase D close / explicit publish approval)
- No iwxxm-validate / tac2iwxxm bump this cycle

## Rollback

- Redeploy prior GHCR digest (`…-8b3a450`) for API then frontend
- Re-run `verify_connectivity.sh` + `/health` + catalog GET
- No DB migrations this cycle — image-only rollback

## Verdict

**T5.10 / 13-deploy-smoke complete.** F15 lint registry + catalog API + workbench catalog UX live on Render.
