# Deploy Checklist

> Generated: 2026-06-24  
> Status: **strategy verified — deploy blocked** (operator gates pending)  
> Deployment plan: [docs/deploy.md](../../../deploy.md)  
> Session: S004-issue-555-feedback | Evolve cycle: EV-004 | Branch: `feat/S004-issue-555-feedback`  
> Prior baseline: [S003 deploy-checklist](../../S003-supabase-keys-config/reports/deploy-checklist.md)

## Scope (S004 / EV-004 delta)

This checklist covers **F5 work sessions** + **#555 UX delta** on top of the **S003 config/key-rotation** path. No topology change — same two Render services (`metar-to-iwxxm-api` + `metar-to-iwxxm-frontend-v4-web`).

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `apps/backend` | `/api/v1/work-sessions`, `/admin/work-sessions` routes | **Redeploy API** (Docker image) |
| `apps/frontend` | Work history UI, #555 error log / replace-results UX | **Rebuild static site** |
| Supabase | `20250623000007_metar_work_sessions.sql` + advisor `003`–`006` | **Operator** — `supabase db push` or dashboard |
| Render secrets | S003 canonical keys (`SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY`) | **Operator** — [env-sync-runbook.md](../../../env-sync-runbook.md) |
| Connectivity | H4 CORS + H5 `/config.json` + T3 live auth | **Verify after redeploy** |

## Pre-Deploy

- [x] Configuration complete (repo) — `config/prod.json`, `render.yaml`, Dockerfile `COPY config/` present
- [ ] All secrets configured on Render — **FAIL (operator pending)** — live frontend still serves legacy `anon` JWT in `/config.json`
- [x] Data assets staged — N/A (schemas in API image; F5 data in Supabase migrations)
- [x] Resource allocation verified — API: starter, 1 instance, `/health`; frontend: static CDN
- [x] Rollback plan reviewed — user approved 2026-06-24
- [x] H0c CORS unit tests pass — `uv run pytest tests/unit/test_cors_policy.py` (**6/6 PASS**)
- [x] Frontend config ↔ API URL matrix — `config/prod.json` canonical; `staging-secrets-matrix.md` superseded (ADR-010)
- [x] `api.corsOrigins` in `config/prod.json` — matches v4 frontend origin
- [x] Post-deploy H4–H5 command documented — `bash scripts/deploy/verify_connectivity.sh` / `make test-live-connectivity`

### Agent verification results (2026-06-24)

| Check | Agent | Result | Notes |
|-------|-------|--------|-------|
| Configuration | Agent 1 | **PASS** | `render.yaml` static+api; `METAR_CONFIG_ENV=prod`; Dockerfile includes `COPY config config` (S003 fix merged) |
| Secrets | Agent 2 | **FAIL (Render)** | Cannot verify dashboard remotely; live `/config.json` publishable key is legacy JWT (`eyJ…`, role `anon`), not `sb_publishable_*` |
| Data/Volumes | Agent 3 | **PARTIAL** | `vendor/schemas` in image ✓; F5 migration SQL in repo — **operator apply (T1.3) not confirmed** |
| Resources | Agent 4 | **PASS** | starter plan, `numInstances: 1`, health `/health`, bind `0.0.0.0:$PORT` |
| Template deploy | Agent 5 | **PASS** | `static+api` template; `render.yaml` matches; CI deploys API Docker + frontend hook (dual path vs Blueprint static — documented) |
| Connectivity | Agent 6 | **PARTIAL** | H0c **6/6 PASS**; H4 **FAIL** (400 Disallowed CORS origin); H5 **PASS** (`/config.json` `api.baseUrl` correct) |

### Live staging verification (2026-06-24)

| Tier | Command | Result |
|------|---------|--------|
| API health | `GET /health` | **PASS** |
| H0c | `pytest tests/unit/test_cors_policy.py` | **6/6 PASS** |
| H4 | OPTIONS from `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | **FAIL** — `400 Disallowed CORS origin` (work-sessions PATCH preflight also fails) |
| H5 | `GET /config.json` → `api.baseUrl` | **PASS** — matches `https://metar-to-iwxxm-api.onrender.com` |
| T3 live auth | `make test-live` | **BLOCKED** — H4 + legacy keys |

**Root cause (H4):** Deployed API image likely predates S003 `config/prod.json` CORS wiring, or `METAR_CORS_ORIGINS` was removed before API redeploy with baked config. Frontend already on S003 `/config.json` model; API CORS list does not include v4 frontend origin at runtime.

### Blocking items before deploy

1. **Operator T1.3** — Apply Supabase migrations `003`–`006` + `20250623000007_metar_work_sessions.sql` on METAR project.
2. **Operator S003** — Complete [env-sync-runbook.md](../../../env-sync-runbook.md): rotate to `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` on both Render services.
3. **Redeploy API** — Merge S004 to `main` (or deploy branch) so F5 routes + `config/prod.json` CORS are live.
4. **Rebuild frontend** — `prepare-config.sh` injects rotated publishable key into `/config.json`.
5. **Verify H4–H5** — `make test-live-connectivity` with `LIVE_*` from `config/prod.json` → `liveE2e.*`.
6. **T3 signoff** — `make test-live` (UJ-001, UJ-004 waived from 11; run after H4 green).

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Docker image build failure | CI builds on PR; Dockerfile HEALTHCHECK; `uv sync --frozen` | approved |
| 2 | Secret missing at runtime (rotated keys) | Pre-deploy dashboard checklist; `make env-check METAR_CONFIG_ENV=prod LIVE=1` | approved |
| 3 | F5 migration not applied — 500 on work-sessions | Apply `20250623000007` before API deploy; run `pytest tests/integration/test_metar_work_sessions_migration.py` locally | approved |
| 4 | Auth/CORS break when removing legacy env vars | Deploy API with `config/` baked in first; keep legacy `METAR_CORS_ORIGINS` until H4 pass; then remove per runbook | approved |
| 5 | Frontend stale `/config.json` (wrong publishable key) | Redeploy static after API secrets set; `prepare-config.sh` injects key at build | approved |
| 6 | H4 false-pass on old CORS env | After redeploy, run `verify_connectivity.sh` including work-sessions PATCH preflight | approved |
| 7 | Render cold start / spin-down | `verify_connectivity.sh` wake retries (3×30s) | approved |
| 8 | F5 pg_cron retention misconfigured | ADR-012: verify cron job in migration; monitor Supabase advisors post-deploy | approved |

## Rollback

- **Command:** Render Dashboard → service → Deploys → Rollback to previous deploy
- **Procedure:**
  1. Identify last known good deploy in Render history (current live: pre-S004, H4 already failing)
  2. Roll back **metar-to-iwxxm-api** if auth/CORS/F5 regression
  3. Roll back **metar-to-iwxxm-frontend-v4-web** if `/config.json` bootstrap fails
  4. Re-enable legacy env vars temporarily if S003 config path fails (`METAR_CORS_ORIGINS`, `VITE_*`)
  5. F5 schema is additive — rollback Render only; do not drop `metar_work_sessions` without operator decision
  6. Run `make test-live-connectivity` with `LIVE_*` from `config/prod.json`
- **Last known good:** API health OK; H4 **failing** on current live (2026-06-24); H5 PASS on `/config.json`
- **Git rollback:** Revert merge on `main`; CI/CD triggers redeploy
- **Supabase keys:** Keep new keys in dashboard; rollback Render deploy only — do not re-enable leaked `service_role` JWT

## Redeploy order (S004 + S003)

1. Merge `feat/S004-issue-555-feedback` to `main` after CI green.
2. **Supabase**: Apply advisor migrations `003`–`006` + `20250623000007_metar_work_sessions.sql`.
3. **Supabase keys**: Rotate publishable + secret; update local `.env`; `make env-check`.
4. Deploy **metar-to-iwxxm-api** with rotated secrets + `METAR_CONFIG_ENV=prod`.
5. Rebuild **metar-to-iwxxm-frontend-v4-web** (publishable key injected into `/config.json`).
6. Run `make test-live-connectivity` (H4–H5), then `make test-live-api` / T3 if credentials available.
7. Remove deprecated Render env vars per runbook Step 3–4 (only after H4 pass).
8. Disable legacy Supabase JWT keys in dashboard only after all services verified.

## Sign-Off

- [x] User approved implementation (11-verify-impl) — 2026-06-24; T3 deferred to this stage
- [x] Deploy strategy verified (this checklist) — 2026-06-24
- [x] User approved failure mitigations — 2026-06-24
- [x] User approved rollback plan — 2026-06-24
- [ ] Ready to deploy (13-deploy-smoke) — **NO** until operator gates + H4 green

## Next step

**13-deploy-smoke** — after operator completes redeploy order above and H4–H5 pass.
