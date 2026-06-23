# Deploy Checklist

> Generated: 2026-06-23  
> Status: **strategy verified — deploy blocked** on Dockerfile fix + Render key rotation  
> Deployment plan: [docs/deploy.md](../../../deploy.md)  
> Session: S003-supabase-keys-config | Bug: [BUG-2026-06-23-supabase-service-key-leak](../../../bug-reports/BUG-2026-06-23-supabase-service-key-leak.md)  
> Branch: `fix/supabase-service-key-leak`

## Scope (S003 delta)

This checklist covers **Supabase key rotation**, **S003 config split** (`config/{local,prod}.json` + runtime `/config.json`), and **deprecated env var removal** on Render. No topology change — same two Render services.

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `packages/shared` | `config_loader.py`, canonical Supabase env helpers | **Redeploy API** (Docker image) |
| `config/prod.json` | CORS, URLs, Supabase URL (non-secrets) | **Must be baked into API image** + frontend build |
| `apps/frontend` | Runtime `/config.json` bootstrap (ADR-010) | **Rebuild static site** with publishable key inject |
| Render secrets | Rotate `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` | **Operator** — [env-sync-runbook.md](../../../env-sync-runbook.md) |
| Deprecated env | Remove `VITE_*`, `METAR_CORS_ORIGINS`, legacy Supabase keys | **Operator** — after redeploy verified |

## Pre-Deploy

- [ ] Configuration complete — **FAIL**: `config/` not copied into API Docker image (`apps/backend/docker/Dockerfile`)
- [ ] All secrets configured — **FAIL (Render)**: key rotation pending; repo docs + `render.yaml` wiring **PASS**
- [x] Data assets staged — N/A (Supabase external; `vendor/schemas` in API image)
- [x] Resource allocation verified — API: starter plan, 1 instance; frontend: static CDN; bind `0.0.0.0:$PORT`
- [x] Rollback plan reviewed — user approved 2026-06-23
- [x] H0c CORS unit tests pass — `uv run pytest tests/unit/test_cors_policy.py` (6/6)
- [ ] Frontend config ↔ API URL matrix complete — **PARTIAL**: `config/prod.json` + `env-contract.md` canonical; `staging-secrets-matrix.md` superseded
- [ ] `api.corsOrigins` in `config/prod.json` documented — **PASS** in git; **FAIL** at API runtime until Docker COPY fixed
- [x] Post-deploy H4–H5 command documented — `bash scripts/deploy/verify_connectivity.sh` / `make test-live-connectivity`

### Agent verification results (2026-06-23)

| Check | Agent | Result | Notes |
|-------|-------|--------|-------|
| Configuration | Agent 1 | **FAIL** | S003 model in code; `config/` missing from API image; CI frontend Docker path vs `render.yaml` static |
| Secrets | Agent 2 | **FAIL (Render)** | Rotation deferred from stage 11; repo blueprint **PASS** |
| Data/Volumes | Agent 3 | **N/A** | No Modal volumes; schemas in Docker image |
| Resources | Agent 4 | **PASS** | starter plan, `numInstances: 1`, health `/health` |
| Template deploy | Agent 5 | **PARTIAL** | `static+api` in `render.yaml`; CI `ci-cd.yml` still uses deprecated `FRONTEND_VITE_*` + Docker frontend hook |
| Connectivity | Agent 6 | **PARTIAL PASS** | H0c 6/6; CORS via inline `CORSMiddleware` + `get_cors_origins()` (not shared `configure_cors` helper); H4/H5 not re-run this session |

### Blocking items before deploy

1. **Code fix**: Add `COPY config/ config/` to `apps/backend/docker/Dockerfile` so `METAR_CONFIG_ENV=prod` resolves `/app/config/prod.json`.
2. **Operator**: Complete [env-sync-runbook.md](../../../env-sync-runbook.md) Steps 1–4 — rotate Supabase keys on both Render services.
3. **Operator**: Remove deprecated Render env vars only **after** redeploy + H4/H5 pass (otherwise CORS/auth may break mid-migration).
4. **Advisory**: Align CI deploy with `render.yaml` static build (or document intentional dual path); update H5 to check `/config.json` not VITE bundle embed.

### Live staging baseline (pre-S003 merge)

| Check | Status |
|-------|--------|
| API health | Last verified 2026-06-22 — `GET /health` healthy |
| H4 CORS preflight | PASS (legacy `METAR_CORS_ORIGINS` likely still set on Render) |
| H5 bundle URL | PASS (pre-S003 VITE-centric check) |
| S003 runtime `/config.json` on live | **NOT YET** — requires merge + frontend rebuild |
| Rotated Supabase keys on live | **NOT YET** — explicit stage-11 deferral |
| T3 live auth (UJ-003) | **BLOCKED** — run after key rotation (`make test-live`) |

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Docker image build failure | CI builds on PR; Dockerfile HEALTHCHECK; `uv sync --frozen` | approved |
| 2 | Secret missing at runtime (rotated keys) | Pre-deploy dashboard checklist; `make env-check METAR_CONFIG_ENV=prod LIVE=1` | approved |
| 3 | **`config/prod.json` absent in API container** | Add `COPY config/ config/` before deploy; verify CORS from config not legacy env | approved — fix before deploy |
| 4 | Auth/CORS break when removing legacy env vars | Deploy API with config baked in first; keep legacy vars until H4 pass; then remove | approved |
| 5 | Frontend stale `/config.json` (wrong publishable key) | Redeploy static after API secrets set; `prepare-config.sh` injects key at build | approved |
| 6 | CI vs Blueprint deploy path split | Prefer `render.yaml` static buildCommand; retire Docker frontend deploy hook when ready | approved |
| 7 | Render cold start / spin-down | `verify_connectivity.sh` wake retries (3×30s) | approved |
| 8 | H5 false-fail on S003 model | Update H5 to fetch live `/config.json` and assert `api.baseUrl` | advisory |

## Rollback

- **Command:** Render Dashboard → service → Deploys → Rollback to previous deploy
- **Procedure:**
  1. Identify last known good deploy in Render history (pre-S003 merge / pre-key-rotation)
  2. Roll back **metar-to-iwxxm-api** if auth/CORS/config regression
  3. Roll back **metar-to-iwxxm-frontend-v4-web** if `/config.json` bootstrap fails
  4. Re-enable legacy env vars temporarily if S003 config path fails (`METAR_CORS_ORIGINS`, `VITE_*`)
  5. Run `make test-live-connectivity` with `LIVE_*` from `config/prod.json` → `liveE2e.*`
- **Last known good:** Current live staging (pre-S003 merge on `main`; legacy env vars)
- **Git rollback:** Revert merge on `main`; CI/CD triggers redeploy
- **Supabase keys:** Keep new keys in dashboard; rollback Render deploy only — do not re-enable leaked `service_role` JWT

## Redeploy order (S003)

1. Merge `fix/supabase-service-key-leak` to `main` after CI green (includes Docker `config/` fix).
2. **Supabase**: Create new publishable + secret keys; update local `.env`.
3. Deploy **metar-to-iwxxm-api** with rotated secrets + `METAR_CONFIG_ENV=prod`.
4. Rebuild **metar-to-iwxxm-frontend-v4-web** (publishable key injected into `/config.json`).
5. Run `make test-live-connectivity` (H4–H5), then `make test-live-api` / T3 auth if credentials available.
6. Remove deprecated Render env vars per runbook Step 3–4.
7. Disable legacy Supabase JWT keys in dashboard (Step 1.7) only after all services verified.

## Sign-Off

- [x] User approved implementation (11-verify-impl) — 2026-06-23; T3 auth deferred to this stage
- [x] Deploy strategy verified (this checklist) — 2026-06-23; user approved mitigations + rollback
- [ ] Ready to deploy — blocked on Docker `config/` COPY + Render key rotation (operator)

## References

- [verify-impl.md](verify-impl.md) — stage 11 approval
- [env-sync-runbook.md](../../../env-sync-runbook.md) — operator sync steps
- [env-contract.md](../../../env-contract.md) — canonical secret names
- [config-spec.md](../../../config-spec.md) — S003 config schema
- Prior checklist: [S002 deploy-checklist](../../S002-issue-594-feedback/reports/deploy-checklist.md)
