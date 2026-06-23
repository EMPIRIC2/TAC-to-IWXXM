# Deploy Checklist

> Generated: 2026-06-22  
> Status: **ready** (delta deploy — S002 / EV-003 / GitHub #594)  
> Deployment plan: [docs/deploy.md](../../../deploy.md)  
> Session: S002-issue-594-feedback | Evolve: EV-003 | PR: [#685](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/685)

## Scope (delta)

This checklist covers the **S002 COR-after-time decode fix + Source TAC traceability** delta on branch `fix/S002-issue-594-feedback`. No new deployables, secrets, or topology changes — **both API and frontend** must redeploy because the change spans GIFTs (in API image), API schema (`tac_input`), and frontend UI.

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `packages/gifts` | ICAO COR-after-time grammar fix | Included in API Docker image — **redeploy metar-api** |
| `apps/backend` | `ConversionResult.tac_input` field | **Redeploy metar-api** |
| `apps/frontend` | Source TAC panel per result | **Rebuild static site** |
| Auth/CORS | Pre-existing wiring | Verify H4–H5 post-redeploy; no CORS var changes |

**Pre-merge note:** PR #685 is open; live staging currently runs pre-S002 code. H4/H5 below verify **existing** connectivity wiring, not S002 feature behavior.

## Pre-Deploy

- [x] Configuration complete — `render.yaml` matches static+api template (API Docker + static frontend)
- [x] Secrets documented — `docs/staging-secrets-matrix.md`; dashboard-only: `SUPABASE_*`, `DATABASE_URL`
- [x] Data assets staged — N/A (Supabase external; vendor/schemas in Docker image)
- [x] Resource allocation verified — API: starter plan, 1 instance; frontend: static CDN
- [x] Rollback plan reviewed — user approved 2026-06-22
- [x] H0c CORS unit tests pass — `uv run pytest tests/unit/test_cors_policy.py` (6/6)
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
| Connectivity | Agent 6 | **PASS** | H0c 6/6, H4 PASS, H5 PASS on live Render (pre-S002 baseline) |

### Live staging state (verified 2026-06-22)

| Check | Status |
|-------|--------|
| API health | `GET /health` → healthy |
| H4 CORS preflight | PASS |
| H5 bundle URL | Bundle references `https://metar-to-iwxxm-api.onrender.com` |
| S002 COR-after-time on live | **NOT YET** — requires merge + API redeploy |
| S002 Source TAC UI on live | **NOT YET** — requires merge + frontend rebuild |

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Docker image build failure (GIFTs change in API image) | CI builds on PR; Dockerfile HEALTHCHECK; layer-cached `uv sync` | approved |
| 2 | Secret missing at runtime | Pre-deploy dashboard checklist; `DISABLE_AUTH=false` in blueprint | approved |
| 3 | Auth/CORS / browser connectivity | `METAR_CORS_ORIGINS` + H4/H5 gates; redeploy API before frontend on CORS change | approved |
| 4 | Render cold start / spin-down | `wake_live_api` in verify_connectivity.sh (3×30s retry) | approved |
| 5 | Stale frontend bundle (Source TAC UI missing) | Rebuild frontend after merge; H5 checks bundle API URL | approved |
| 6 | GIFTs decoder regression on edge COR patterns | Bug repro tests + GIFTs unit tests in CI; T3 COR-after-time smoke post-deploy | approved |

## Rollback

- **Command:** Render Dashboard → service → Deploys → Rollback to previous deploy
- **Procedure:**
  1. Identify last known good deploy in Render history (pre-#685 merge)
  2. Roll back **metar-to-iwxxm-api** if COR decode regression
  3. Roll back **metar-to-iwxxm-frontend-v4-web** if Source TAC UI regression
  4. Run `bash scripts/deploy/verify_connectivity.sh` with `LIVE_*` env vars
- **Last known good:** `main` pre-PR #685 merge (current live staging)
- **Git rollback:** Revert merge commit on `main` and push; CI/CD triggers redeploy

## Redeploy order (S002 delta)

1. Merge PR #685 to `main` after CI green.
2. Deploy **metar-to-iwxxm-api** (GIFTs + `tac_input` API change).
3. Rebuild **metar-to-iwxxm-frontend-v4-web** (Source TAC UI).
4. Run connectivity verification:

   ```bash
   export LIVE_API_URL="https://metar-to-iwxxm-api.onrender.com"
   export LIVE_FRONTEND_URL="https://metar-to-iwxxm-frontend-v4-web.onrender.com"
   export VITE_API_BASE_URL="${LIVE_API_URL}"
   bash scripts/deploy/verify_connectivity.sh
   ```

5. T3 signoff (ADV-002): verify COR-after-time conversion + Source TAC panel on live Render:

   ```bash
   make test-live-e2e   # H6 Playwright — UJ-001 #594 delta
   ```

## Sign-Off

- [x] User approved implementation (11-verify-impl) — UJ-001 + F1 delta (TC-001b) approved
- [x] Deploy strategy verified (this checklist) — user approved 2026-06-22
- [x] Connectivity wiring ready for 13-deploy-smoke (H4–H5 verified on current staging)
- [x] User approved deploy strategy (stage 12) — proceed to 13 after merge
- [x] Ready to deploy — **yes** after PR #685 merge; proceed to **13-deploy-smoke**

## Deploy gate summary

| Gate | Status |
|------|--------|
| QA (09) | PASS (S002) |
| E2E T0+T2 (10) | PASS (S002) |
| Implementation verified (11) | APPROVED |
| Deploy strategy (12) | **PASS** (infra + connectivity wiring) |
| PR merge | OPEN — [#685](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/685) |
| Next | **13-deploy-smoke** — T3 COR-after-time + Source TAC on Render post-merge |
