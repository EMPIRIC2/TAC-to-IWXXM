# Deploy & Smoke — S019 / EV-014 (T6.6 / 13-deploy-smoke)

> Date: 2026-07-21T16:24Z  
> Status: **PARTIAL** — H0c + H1 (public) + H4 + H5 **PASS**; authenticated H3 / live Render allowlist / live BYOC **BLOCKED**  
> Branch: `cursor/s019-t66-deploy-smoke-151c` (from tip `cursor/s019-t64-verify-build-7820` @ `7fba0a5`)  
> Open stack: [#771](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/771) M5+M6 T6.1–T6.5 (CI green, not merged)  
> Agent: cloud run without private-worker `.env` / Render MCP auth  
> Follow-up: local/CI allowlist recommendation applied in `.env.example` + corpus docs; **live Render env not changed** (`RENDER_API_KEY` deferred)

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
| Allowlist local/CI docs | **PASS** | `.env.example` + deploy/env-contract set recommended `wis2box,127.0.0.1,127.0.0.0/8,localhost` |
| Allowlist live Render value | **DEFERRED** | No `RENDER_API_KEY` this session — leave Render empty (fail-closed) until BYOC hosts known |
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

## Proceeding without `RENDER_API_KEY` (operator approved)

| Action | Status |
|--------|--------|
| Document + set local/CI recommended allowlist in `.env.example` / corpus | **Done** |
| Change live Render `DISSEMINATION_EGRESS_ALLOWLIST` | **Skipped** — keep empty fail-closed until API key + exact BYOC hosts |
| Authenticated H3 / live BYOC | **Still blocked** — needs `E2E_USER_*` (admin login) + destination hosts |

## Remaining blockers (T6.6 → completed / cycle close)

1. **Provide `.env` (or private-worker secrets)** with `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` (admin login) and live BYOC destinations for **Postgres + WIS2 + EDIS** (memory-only).
2. **Optional later:** `RENDER_API_KEY` to set/confirm live allowlist to exact demo hostnames before BYOC.
3. **Merge #771** → wait for GHCR + Render API/FE redeploy (drawer on live bundle).
4. Re-run: authenticated H3 → live BYOC preflight/send evidence → optional F19 waive.

## Rollback

- Image-only: redeploy prior GHCR digests for API then frontend (no DB migration in M6).
- Re-run `verify_connectivity.sh` + `/health`.

## Verdict

**Connectivity half of T6.6 PASS** (H0c + H1 public + H4 + H5).  
**Local/CI allowlist recommendation applied** (docs + `.env.example`).  
**T6.6 overall remains blocked** on auth + live BYOC (+ optional Render allowlist set when API key available; FE drawer after #771).

## Update 2026-07-21T17:50Z (post-#771 merge)

| Check | Result |
|-------|--------|
| PR #771 | **MERGED** `2bbe9f5` — CI/CD Pipeline + Deploy **success** |
| Live FE drawer | **PASS** — `/assets/App-C1eOPfC1.js` contains `dissemination` / `preflight` / `open-dissemination` (drawer is code-split; index chunk alone is insufficient probe) |
| Auth H3 / live BYOC | Was blocked — superseded by mock waive below |

## Update 2026-07-21T18:00Z — mock BYOC unblock (`D-S019-EV014-Q15-mock-waive`)

Operator authorized **mock credentials / mock DB / mocked WIS2+EDIS** instead of live
destination services. Secrets stay in gitignored `.env` only (never committed).

| Check | Result |
|-------|--------|
| Mock `.env` | **Created locally** (`E2E_USER_*` / `ADMIN_*` placeholders + local allowlist) — gitignored |
| Fixture shapes | `docs/sessions/S019-dissemination-upload/fixtures/mock-byoc-destinations.json` |
| `make test-mock-byoc-smoke` | **PASS** — **134** tests (SQLite stand-in + WIS2 mocks + EDIS mocks + F19 stubs + API unit) |
| Compose wis2box / Testcontainers PG | **Skipped** this env (no Docker); covered when Docker available via same script |
| Live H3 auth against Render | **Waived** — fake login cannot authenticate Supabase; API unit uses `DISABLE_AUTH` + mocked user |
| Live destination BYOC | **Waived** per Q15/Q21 amendment |

### Final T6.6 verdict

**COMPLETED** with advisories: public H0c/H1/H4/H5 + live FE drawer + mock BYOC close-gate
evidence. Live authenticated H3 and live Postgres/WIS2/EDIS demos deferred indefinitely for
EV-014 under `D-S019-EV014-Q15-mock-waive`.
