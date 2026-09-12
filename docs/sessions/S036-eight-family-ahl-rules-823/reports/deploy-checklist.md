# Deploy Checklist — S036 / EV-029 (Stage 12 / T12.5)

> Generated: 2026-08-02  
> Status: **READY** — `D-S036-12` = 1,1,1 (mitigations + rollback + gate)  
> Deployment plan: [docs/deploy.md](../../../deploy.md)  
> Session: S036-eight-family-ahl-rules-823 · Evolve: EV-029  
> PR: [#828](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/828) · tip `a8e5a5d`  
> Lock: **E29-T6** — API redeploy; H1–H3; **H4–H5 required** (FE Examples unlocked)

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `packages/tac2iwxxm` | Eight-family AHL/`reportStatus` + SWXA encode (0.2.3) | In API image — **redeploy API** |
| `packages/tac-validate` | SWXA registry + family lint deepen | In API image — **redeploy API** |
| `packages/iwxxm-validate` | XSD+SCH consumers (no new deployable) | Via API image |
| `apps/backend` | Additive `product=swxa` | **Redeploy API** |
| `apps/frontend` | Examples unlock `spacewx-A7-3` (SWXA) | **Rebuild static FE** |
| Auth/CORS | Unchanged origins | Re-verify H4–H5 post-deploy |
| Worker / dissemination | No auto-push; AHL helpers only | No worker redeploy required for this cycle |
| Secrets / DB | None new | N/A |

**Pre-merge:** Staging still on `main` @ recorded deploy; EV-029 lands after merge of #828.

## Pre-Deploy

- [x] Configuration complete — `render.yaml` static+api+worker; no new services
- [x] Secrets documented — `docs/ops/staging-secrets-matrix.md` (no new keys for F28/`swxa`)
- [x] Data assets staged — N/A (vendor schemas in image)
- [x] Resource allocation verified — API starter / FE static (unchanged)
- [x] Rollback plan reviewed — user approved 2026-08-02 (`D-S036-12` Q2=1)
- [x] H0c CORS unit tests pass — `pytest tests/unit/test_cors_policy.py` **6/6** (2026-08-02)
- [x] Frontend `VITE_*` ↔ API URL matrix complete — staging-secrets-matrix.md
- [x] `METAR_CORS_ORIGINS` documented — `https://metar-to-iwxxm-frontend-v4-web.onrender.com`
- [x] Post-deploy H4–H5 command documented — `bash scripts/deploy/verify_connectivity.sh`
- [x] Connectivity scripts present — `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py`

### Agent verification results (2026-08-02)

| Check | Agent | Result | Notes |
|-------|-------|--------|-------|
| Configuration | 1 | **PASS** | No Blueprint topology change; additive API enum + FE catalog |
| Secrets | 2 | **PASS** | No new Render secrets for `product=swxa` |
| Data/Volumes | 3 | **N/A** | Schemas baked into API image |
| Resources | 4 | **PASS** | Unchanged starter / static |
| Template deploy | 5 | **PASS** | `static+api+worker`; GHCR image path `ghcr.io/empiric2/tac-to-iwxxm/*` |
| Connectivity | 6 | **PASS** (wiring) | H0c 6/6; live H4–H5 reserved for **T12.6 / 13** |

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Docker/GHCR image build failure | CI builds on PR #828; image-based Render deploy | **approved** |
| 2 | Secret missing at runtime | No new secrets; existing matrix | **approved** |
| 3 | `product=swxa` / AHL regression on live | T0/T1 smokes + product-order + report-state matrix; post-deploy H1–H3 convert/lint | **approved** |
| 4 | Auth/CORS / browser connectivity | No origin changes; **H4–H5 required** at 13 (`verify_connectivity.sh`) | **approved** |
| 5 | Stale FE bundle (SWXA Examples missing) | Redeploy FE after merge; catalog Vitest + H5 URL check | **approved** |
| 6 | Render cold start | `wake_live_api` in `verify_connectivity.sh` (3×30s) | **approved** |
| 7 | Soft residuals (#829 / A7-4/A7-5) leak as silent gaps | Child-issued; not blocking deploy; document in smoke report | **approved** |

## Rollback

- **Command:** Render Dashboard → service → Deploys → Rollback to previous deploy  
  (or pin prior `ghcr.io/empiric2/tac-to-iwxxm/{backend,frontend}:<prior-tag>`)
- **Procedure:**
  1. Identify last known good deploy on `main` (pre-#828 merge)
  2. Roll back **metar-to-iwxxm-api** if convert/lint/`swxa` regresses
  3. Roll back **metar-to-iwxxm-frontend-v4-web** if Examples catalog regresses
  4. Re-run `bash scripts/deploy/verify_connectivity.sh` + `GET /health`
- **Data:** No DB migrations this cycle — image-only rollback
- **Git:** Revert merge commit on `main` and push → CI rebuilds images
- **Last known good:** Current staging `main` deploy (pre-#828)

## Redeploy order (EV-029 / T12.6)

1. Merge PR [#828](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/828) to `main` after CI green (user approval).
2. Deploy **metar-to-iwxxm-api** (new GHCR `backend:main-latest`).
3. Rebuild **metar-to-iwxxm-frontend-v4-web** (SWXA Examples).
4. Run:

   ```bash
   export LIVE_API_URL="https://metar-to-iwxxm-api.onrender.com"
   export LIVE_FRONTEND_URL="https://metar-to-iwxxm-frontend-v4-web.onrender.com"
   export VITE_API_BASE_URL="${LIVE_API_URL}"
   bash scripts/deploy/verify_connectivity.sh   # H0c + H4 + H5
   # then H1–H3 API smokes + UJ-043 / TC-EV029-008 Examples spot-check
   make test-live-connectivity
   ```

5. Record results in T12.6 / 13-deploy-smoke report.

## Sign-Off

- [x] User approved implementation (11-verify-impl) — `D-S036-11` = 2,1,1,1
- [x] Deploy strategy verified (this checklist) — `D-S036-12` = **1,1,1** (2026-08-02)
- [x] Ready for T12.6 / 13-deploy-smoke

**Next:** Merge [#828](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/828) (user approval) → API + FE redeploy → H1–H5 / TC-EV029-008.
