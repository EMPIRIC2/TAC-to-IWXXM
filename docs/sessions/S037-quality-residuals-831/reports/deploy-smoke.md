# Deploy smoke — S037 / EV-030 (T4.4 / 13)

> Status: **PASS** (pending user close approval)  
> Date: 2026-08-03  
> Decision: **D-S037-11/12** = 1 (approve + start 13); merge authorized by same  
> PR: [#832](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/832) **merged**  
> Merge commit: `8bd111c`  
> Main CI tests: [30826197508](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30826197508) — jobs green; **Deploy hook 500** (workaround below)  
> API deploy: `dep-d9ob293l550s73a65rfg` **live** (`backend:20260803151459-8bd111c`)  
> FE deploy: `dep-d9ob2brm8hqs73fu8k2g` **live** (`frontend:20260803151459-8bd111c`)

## Scope

F29 quality-matrix harness + #829 TC SIGMET deepen (A6-2-TC `wmoReference`) + #820 VAA/TCA
decode deepen + `tac2iwxxm` **0.2.4**.

| Surface | URL |
|---------|-----|
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API | https://metar-to-iwxxm-api.onrender.com |

## Results

| Tier | Command / check | Result |
|------|-----------------|--------|
| Main CI Validate/Tests | run 30826197508 | **PASS** |
| Main CI Deploy hook | Render deploy hook + imgURL | **FAIL 500** — images built; API redeploy via Render REST |
| API Render | `dep-d9ob293l550s73a65rfg` live | **PASS** |
| FE Render | `dep-d9ob2brm8hqs73fu8k2g` live | **PASS** |
| H1 | `GET /health` 200 + `tac2iwxxm_available` | **PASS** |
| H0c | CORS unit (6) | **PASS** |
| H3 | `make test-live-api` | **PASS** 13 passed / 8 skipped (auth retired F21) |
| H4 | Live CORS preflight (2) | **PASS** |
| H5 | `/config.json` → live API host | **PASS** |
| TC-EV030-005 FE | App chunk `App-Bhd6UU87.js` contains `sigmet_a6_2_tc` / `sigmet-A6-2-TC` / `wmoReference` | **PASS** |

### Live commands

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
make test-live-connectivity   # H0c + H4 + H5
make test-live-api            # H3
```

### Deploy workaround

CI Deploy step: `curl` deploy hook returned **500**. Images were pushed to GHCR
(`…:20260803151459-8bd111c`). Manual:

```text
POST /v1/services/{id}/deploys  {"imageUrl": "ghcr.io/empiric2/tac-to-iwxxm/{backend,frontend}:TAG"}
```

## Health

- API healthy; `tac2iwxxm_available: true`
- FE `/config.json` points at live API; Examples include TC SIGMET A6-2-TC reference
- Auth login skips expected under F21 public app

## Rollback

- Pin prior GHCR tags (e.g. `…:20260803002330-5efe438`) via Render `POST …/deploys` with `imageUrl`
- Re-run `make test-live-connectivity` + `/health`

## Verdict

**T4.4 / 13-deploy-smoke PASS** (H1–H5 + FE catalog unlock). Ready for **T4.5** closeout
(#831 / evolve summary / F29 → Done) pending user approve close.
