# Deploy Checklist

> Generated: 2026-06-22  
> Status: **ready** (delta deploy — S001 / EV-001 / GitHub #656)  
> Deployment plan: [docs/deploy.md](../../../deploy.md)  
> Session: S001-convert-send-buttons | Evolve: EV-001

## Scope (delta)

This checklist covers the **S001 Convert & Convert&Send** frontend delta merged to `main` via PR #683 (`220ad64`). No new deployables, secrets, or topology changes — static frontend rebuild required to surface UI changes.

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `apps/frontend` | Convert + Convert&Send buttons (#656) | Rebuild static site (or confirm auto-deploy from main) |
| `apps/backend` | No S001 API changes | No redeploy required unless drift detected |
| Auth/CORS | Pre-existing wiring | Verify H4–H5 post-frontend deploy |

## Pre-Deploy

- [x] Configuration complete — `render.yaml` matches static+api template (API Docker + static frontend)
- [x] Secrets documented — `docs/ops/staging-secrets-matrix.md`; dashboard-only: `SUPABASE_*`, `DATABASE_URL`
- [x] Data assets staged — N/A (Supabase external; vendor/schemas in Docker image)
- [x] Resource allocation verified — API: starter plan, 1 instance; frontend: static CDN
- [x] Rollback plan reviewed — Render dashboard rollback (see below)
- [x] H0c CORS unit tests pass — `pytest tests/unit/test_cors_policy.py` (6/6)
- [x] Frontend `VITE_*` ↔ API URL matrix complete — staging-secrets-matrix.md
- [x] `METAR_CORS_ORIGINS` documented — `https://metar-to-iwxxm-frontend-v4-web.onrender.com`
- [x] Post-deploy H4–H5 command documented — `bash scripts/deploy/verify_connectivity.sh`

### Agent verification results (2026-06-22)

| Check | Agent | Result | Notes |
|-------|-------|--------|-------|
| Configuration | Agent 1 | **PASS** | `render.yaml`: API Dockerfile, static frontend, health `/health`, env vars wired |
| Secrets | Agent 2 | **PASS** | Blueprint documents required vars; Supabase/DB dashboard-only (`sync: false`) |
| Data/Volumes | Agent 3 | **N/A** | No Modal volumes; schemas baked into API image |
| Resources | Agent 4 | **PASS** | starter plan, `numInstances: 1`, `0.0.0.0:$PORT` via Dockerfile |
| Template deploy | Agent 5 | **PASS** | static+api: two Render services; auth merged in API (ADR-002) |
| Connectivity | Agent 6 | **PASS** | H0c 6/6, H4 PASS, H5 PASS on live Render |

### Live staging state (verified 2026-06-22)

| Check | Status |
|-------|--------|
| API health | `GET /health` → healthy |
| Auth routes | `/auth/login`, `/auth/register`, … present in OpenAPI |
| H4 CORS preflight | PASS |
| H5 bundle URL | Bundle references `https://metar-to-iwxxm-api.onrender.com` |
| S001 UI on frontend | `Convert&Send` present in live JS bundle |

**Note:** E2E-002 (auth absent on staging) from 2026-06-20 is **resolved** — auth routes now live.

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Docker image build failure | CI builds on PR; Dockerfile HEALTHCHECK; layer-cached uv sync | approved (default) |
| 2 | Secret missing at runtime | Pre-deploy dashboard checklist; `DISABLE_AUTH=false` in blueprint | approved (default) |
| 3 | Data/volume mount failure | N/A — schemas COPY'd into image; `ln -s vendor/schemas schemas` | N/A |
| 4 | Auth/CORS / browser connectivity | `METAR_CORS_ORIGINS` + H4/H5 gates; redeploy API before frontend on CORS change | approved — verified live |
| 5 | Render cold start / spin-down | `wake_live_api` in verify_connectivity.sh (3×30s retry) | approved (default) |
| 6 | Stale frontend bundle | Rebuild frontend after API URL change; H5 checks bundle | approved — H5 PASS |

## Rollback

- **Command:** Render Dashboard → service → Deploys → Rollback to previous deploy
- **Procedure:**
  1. Identify last known good deploy in Render history
  2. Roll back **metar-to-iwxxm-frontend-v4-web** first (if UI regression)
  3. Roll back **metar-to-iwxxm-api** if API regression
  4. Run `bash scripts/deploy/verify_connectivity.sh` with `LIVE_*` env vars
- **Last known good:** `main` @ `220ad64` — Merge PR #683 (S001 Convert&Send)
- **Git rollback:** Revert commit on `main` and push; CI/CD triggers redeploy

## Redeploy order (S001 delta)

1. Confirm `main` includes PR #683 (merged).
2. Trigger or confirm **metar-frontend** static site rebuild from `main`.
3. API redeploy only if backend drift detected (not required for S001).
4. Run connectivity verification:

   ```bash
   export LIVE_API_URL="https://metar-to-iwxxm-api.onrender.com"
   export LIVE_FRONTEND_URL="https://metar-to-iwxxm-frontend-v4-web.onrender.com"
   export VITE_API_BASE_URL="${LIVE_API_URL}"
   bash scripts/deploy/verify_connectivity.sh
   ```

5. Optional T3 signoff: `make test-live-e2e` (H6 Playwright UJ-001 Convert&Send path).

## Sign-Off

- [x] User approved implementation (11-verify-impl) — S001 UJ-001 paths A/B/C approved
- [x] Deploy strategy verified (this checklist)
- [x] Connectivity ready for 13-deploy-smoke (H4–H5 verified live)
- [ ] User explicit deploy approval — pending (risk prompts skipped; defaults applied)
- [ ] Ready to deploy — **yes** for S001 frontend delta; proceed to **13-deploy-smoke**

## Deploy gate summary

| Gate | Status |
|------|--------|
| QA (09) | PASS (S001) |
| E2E T0+T2 (10) | PASS (S001) |
| Implementation verified (11) | APPROVED |
| Deploy strategy (12) | **PASS** |
| Next | **13-deploy-smoke** — T3 live UJ-001 Convert&Send on Render |
