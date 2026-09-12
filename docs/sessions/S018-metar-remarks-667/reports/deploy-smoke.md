# Deploy & Smoke — S018 / EV-013 (#667)

> Date: 2026-07-20  
> Mode: **validate-existing** + follow-up API fix PR  
> Branch (fix): `cursor/metar-remarks-live-e2e-2e2e` → [#752](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/752)

## Staging topology

| Service | URL | Deployed image / note |
|---------|-----|------------------------|
| API | https://metar-to-iwxxm-api.onrender.com | `backend:…-ccfb8cc` (**#750** live) |
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com | `frontend:…-ccfb8cc` live |

## Feature verification (#667)

| Check | Live now (#750) | After #752 deploy |
|-------|-----------------|-------------------|
| `iwxxm_us` retains `humanReadableText` for unparsed RMK | **PASS** | PASS |
| `annex3` emits `REMARKS_EXCLUDED` in `/api/v1/convert` `issues` | **FAIL** (dropped on success path) | **PASS** (unit green; awaiting merge) |
| Package `tac2iwxxm` REMARKS_EXCLUDED | PASS (in #750 image) | PASS |

**Root cause (live gap):** `convert_metar_tac_with_metadata` discarded tac2iwxxm success-path issues. Fixed in #752.

## Smoke tiers

| Tier | Status | Evidence |
|------|--------|----------|
| H0c | PASS | `test_cors_policy.py` 6/6 |
| H1 | PASS | `/health` 200, `tac2iwxxm_available: true` |
| H3 | PASS | live API health + convert/lint 24/24 |
| H4 | PASS | CORS preflight allows FE origin |
| H5 | PASS | `/config.json` → api.baseUrl = live API |
| UJ-026 live (`iwxxm_us`) | PASS | `test_uj026_live_iwxxm_us_human_readable` |
| UJ-026 live (`annex3`) | FAIL until #752 | empty `issues[]` |
| Playwright UJ-026 | 2 PASS / 1 FAIL | fail = annex3 REMARKS_EXCLUDED (same gap) |

## E2E added

| File | Role |
|------|------|
| `apps/backend/tests/unit/test_uj026_remarks_convert_issues.py` | API unit (PASS locally) |
| `tests/live/test_uj026_metar_remarks_live.py` | Live API gate |
| `apps/e2e/uj026-metar-remarks.e2e.spec.ts` | Playwright API + UI (badge 49→52) |

## Gate status

- **Partial deploy smoke PASS** for connectivity + iwxxm_us retain.
- **Full #667 acceptance on staging** blocked on merge/deploy of **#752**.
- Recommend: merge #752 → wait for Render image `…-<sha>` → re-run live UJ-026 + Playwright annex3 test.

## Commands

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
# + ADMIN_EMAIL / ADMIN_PASSWORD from .env
bash scripts/deploy/verify_connectivity.sh
uv run pytest apps/backend/tests/infrastructure/test_live_api_health.py \
  tests/live/test_t72_h3_live_smoke.py tests/live/test_uj026_metar_remarks_live.py \
  -m live_api -v --no-cov
cd apps/e2e && DISABLE_AUTH=false pnpm exec playwright test uj026-metar-remarks.e2e.spec.ts
```
