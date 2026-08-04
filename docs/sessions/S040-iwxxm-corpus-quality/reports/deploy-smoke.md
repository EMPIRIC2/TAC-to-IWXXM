# Deploy smoke — S040 / EV-032 (T4.5 / 13)

> Status: **PASS** (pending user close approval)  
> Date: 2026-08-04  
> Decision: **D-S040-13** = 1 (push+merge #848 → DOKS redeploy → H1–H5)  
> PR: [#848](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/848) **merged**  
> Merge commit: `dfecba46`  
> Main CI tests: [30953419422](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30953419422) — Validate + all Test jobs **SUCCESS**; **Deploy hook FAIL** (Render suspended — expected post-DOKS cutover)  
> GHCR images: `backend|frontend|worker:20260804214648-dfecba4` (+ `main-latest`)  
> DOKS API: `ghcr.io/empiric2/tac-to-iwxxm/backend:20260804214648-dfecba4` (**live**)  
> DOKS FE: `ghcr.io/empiric2/tac-to-iwxxm/frontend:20260804214648-dfecba4` (**live**)  
> Alembic initContainer: pinned `backend:ev031-doks` (main image lacks `alembic` module — see notes)

## Scope

F32 VONA (+ deepen A6-2-TC / #835, #741, #808/#847 docs). Delta API + static FE on DOKS.

| Surface | URL |
|---------|-----|
| Frontend | https://app.tac-to-iwxxm.com |
| API | https://api.tac-to-iwxxm.com |
| LB | http://168.144.12.70 |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI Validate/Tests | run 30953419422 | **PASS** |
| Main CI Deploy (Render) | suspended service | **FAIL expected** — images pushed to GHCR |
| Supabase Sync | run 30953419405 | **PASS** (incl. `20260804000012_tac_work_sessions_vona`) |
| DOKS API rollout | `kubectl set image` + split init | **PASS** |
| DOKS FE rollout | `frontend:20260804214648-dfecba4` | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) via `verify_connectivity.sh` | **PASS** |
| H2 | Alembic head on live DB | **PASS prior** — `20260803_0001` (unchanged; VONA is Supabase SQL) |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → `https://api.tac-to-iwxxm.com` | **PASS** |
| TC-F32 / VONA convert | live `POST /api/v1/convert` product=vona | **PASS** — `VolcanoObservatoryNoticeForAviation` |
| TC-EV032 FE | `App-BkEPMp_C.js` contains `vona_a7_1` / `vona-A7-1` | **PASS** |

### Live commands

```bash
export LIVE_API_URL=https://api.tac-to-iwxxm.com
export LIVE_FRONTEND_URL=https://app.tac-to-iwxxm.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
```

### DOKS rollout (workaround)

CI Deploy step targets **suspended Render** services and fails after GHCR push. Manual:

```bash
TAG=20260804214648-dfecba4
kubectl -n metar-iwxxm set image deploy/metar-frontend \
  frontend="ghcr.io/empiric2/tac-to-iwxxm/frontend:${TAG}"
# Main backend image has no alembic module; keep init on ev031-doks
kubectl -n metar-iwxxm set image deploy/metar-api \
  api="ghcr.io/empiric2/tac-to-iwxxm/backend:${TAG}" \
  alembic-upgrade="ghcr.io/empiric2/tac-to-iwxxm/backend:ev031-doks"
kubectl -n metar-iwxxm rollout status deploy/metar-api deploy/metar-frontend
```

**Advisory:** bake `alembic` into the main CI backend image (or drop init once migrations are Job-only) so API rollouts do not depend on `ev031-doks`. Tracked as follow-up from EV-031/EV-032 DOKS ops.

## Health

- API healthy; `tac2iwxxm_available: true`
- FE `/config.json` points at DOKS API; Examples bundle includes `vona_a7_1`
- Live VONA convert returns IWXXM VONA root
- Auth login skips expected under F21 public app

## Rollback

```bash
kubectl -n metar-iwxxm set image deploy/metar-api \
  api=ghcr.io/empiric2/tac-to-iwxxm/backend:ev031-doks \
  alembic-upgrade=ghcr.io/empiric2/tac-to-iwxxm/backend:ev031-doks
kubectl -n metar-iwxxm set image deploy/metar-frontend \
  frontend=ghcr.io/empiric2/tac-to-iwxxm/frontend:main-latest   # prior digest / prior tag
# Or pin prior GHCR tag 20260804… from S039 baseline
make test-live-connectivity
```

## Verdict

**T4.5 / 13-deploy-smoke PASS** (H1–H5 + live VONA). Ready for Phase D / evolve closeout pending user approve.
