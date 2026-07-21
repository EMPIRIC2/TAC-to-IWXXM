# Deploy & Smoke — S019 / EV-014 (T6.6 / 13-deploy-smoke)

> Date: 2026-07-21T16:24Z  
> Status: **PARTIAL** — H0c + H1 (public) + H4 + H5 **PASS**; authenticated H3 / allowlist value / live BYOC **BLOCKED**  
> Branch: `cursor/s019-t66-deploy-smoke-151c` (from tip `cursor/s019-t64-verify-build-7820` @ `7fba0a5`)  
> Open stack: [#771](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/771) M5+M6 T6.1–T6.5 (CI green, not merged)  
> Agent: cloud run without private-worker `.env` / Render MCP auth

## Staging topology

| Service | URL | Live note |
|---------|-----|-----------|
| API | https://metar-to-iwxxm-api.onrender.com | Healthy; OpenAPI includes dissemination POST routes |
| Frontend | https://metar-to-iwxxm-frontend-v4-web.onrender.com | `/config.json` → API; **no** dissemination drawer strings in live JS bundle yet |
| Worker | `metar-to-iwxxm-worker` | Not probed (no F8 auto-push; F16–F19 operator-only) |
| wis2box | Compose/CI only | Not a Render service (E14-04) |

## Pre-deploy / merge gate

| Check | Result | Evidence |
|-------|--------|----------|
| T6.5 deploy-checklist | **PASS** | `reports/deploy-checklist.md` |
| PR #771 merge + Render redeploy (FE drawer) | **PENDING** | Live FE asset `index-CwCtZXFO.js` has **0** matches for `dissemination` / `preflight` / `sink_type` |
| `DISSEMINATION_EGRESS_ALLOWLIST` on Render | **BLOCKED** | No `.env` `RENDER_API_KEY`; Render MCP `list_workspaces` → unauthorized |

## Smoke tiers

| Tier | Status | Evidence |
|------|--------|----------|
| H0c | **PASS** | `tests/unit/test_cors_policy.py` 6/6 via `scripts/deploy/verify_connectivity.sh` |
| H1 | **PASS** | `/health` 200; `tac2iwxxm_available: true`; `test_live_api_health` 14 passed / 7 skipped (auth) |
| H2 | **N/A / not run** | No Alembic/DB pool live script invoked this pass |
| H3 (auth paths) | **SKIPPED** | `ADMIN_EMAIL`/`E2E_USER_*` absent — lint/convert live tests skipped |
| H4 | **PASS** | Live CORS OPTIONS from FE origin → `Access-Control-Allow-Origin` (smoke 2/2 + `test_t83_h4_*`) |
| H5 | **PASS** | `/config.json` `api.baseUrl` = `https://metar-to-iwxxm-api.onrender.com` |
| Dissemination API presence | **PASS (route)** | OpenAPI: `POST /api/v1/dissemination/preflight` + `/send`; unauth POST → **401** `Missing authorization credentials` |
| FE drawer live | **FAIL / not deployed** | Drawer code on #771 tip only; not on live bundle |
| Allowlist live value | **BLOCKED** | Cannot read Render env; cannot auth-probe fail-closed vs allowlisted host |
| Live BYOC (Postgres + WIS2 + EDIS) | **BLOCKED** | No operator BYOC destination URIs/creds in this environment (Q15/Q21 close gate) |
| F19 live | Optional | Not attempted |

## Commands run

```bash
export LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
export LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
bash scripts/deploy/verify_connectivity.sh
# → H0c 6/6, H4 2/2, H5 OK

uv run pytest apps/backend/tests/infrastructure/test_live_api_health.py -m live_api -v --no-cov
# → 14 passed, 7 skipped (auth)

uv run pytest tests/live/test_t72_h3_live_smoke.py tests/live/test_t83_h4_h5_connectivity.py \
  -m live_api -v --no-cov
# → 4 passed, 2 skipped (auth)
```

## Blockers (must clear before T6.6 → completed / cycle close)

1. **Provide `.env` (or private-worker secrets)** with at least:
   - `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` (or deprecated `ADMIN_*`)
   - `RENDER_API_KEY` (allowlist confirm) — or paste current `DISSEMINATION_EGRESS_ALLOWLIST` value
   - Live BYOC destinations for **Postgres + WIS2 + EDIS** (memory-only; never commit)
2. **Merge #771** (and close superseded stack #768–#770 as appropriate) → wait for GHCR + Render API/FE redeploy.
3. Re-run: allowlist confirm → authenticated H3 → live BYOC preflight/send evidence (TC-F17-002 / TC-F18-002 / TC-F16 live) → optional F19 waive.

## Rollback

- Image-only: redeploy prior GHCR digests for API then frontend (no DB migration in M6).
- Re-run `verify_connectivity.sh` + `/health`.

## Verdict

**Connectivity half of T6.6 PASS** (H0c + H1 public + H4 + H5).  
**T6.6 overall = blocked** until Render allowlist confirm + authenticated probes + live BYOC close-gate evidence (and FE drawer live after #771).
