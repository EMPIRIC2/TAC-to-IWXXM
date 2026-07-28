# Deploy Checklist — S023 / EV-017 (F21 / F22 / #783)

> Generated: 2026-07-28  
> Branch: `evolve/EV-017-public-app-privacy` @ `489c9bf`  
> Status: **READY** — strategy verified; handoff **13-deploy-smoke**  
> Deployment plan: [`docs/deploy.md`](../../../deploy.md) §Integration / §Rollback  
> Env contract: [`docs/env-contract.md`](../../../env-contract.md)

## Scope (delta)

Public app cutover (F21), privacy center (F22), IndexedDB deepen, Auth secret cleanup.
Platform: **Render** (API + static FE + F8 worker). Not Modal.

## Phase 1 — Pre-deploy checks

### Agent 1 — Configuration

| Item | Status | Notes |
|------|--------|-------|
| `docs/deploy.md` F21 topology | PASS | Public API; no `/auth`; FE `/config.json` |
| `docs/env-contract.md` | PASS | Rate limits + retired Auth keys documented |
| `config/prod.json` CORS | PASS | FE origin in `corsOrigins` (live `/config.json` matches) |
| Gaps / `Needs human input` | none | |

### Agent 2 — Secrets (live Render inventory 2026-07-28)

**API** `metar-to-iwxxm-api` (`srv-d69v688gjchc73cn9kg0`):

| Key | Status | Action |
|-----|--------|--------|
| `DISABLE_AUTH` | **absent** | Done (T7.4) |
| `SUPABASE_PUBLISHABLE_KEY` | **absent** | Done (T7.4) |
| `DISSEMINATION_EGRESS_ALLOWLIST` | PRESENT | Keep |
| `METAR_CONFIG_ENV` | PRESENT (`prod`) | Keep |
| `DATABASE_URL` | PRESENT | Optional ops — keep |
| `SUPABASE_URL` / `SUPABASE_SECRET_KEY` | PRESENT | **Optional cleanup at 13** — unused by public router; worker has own keys |
| `RATE_LIMIT_*` | absent | OK — code defaults apply |

**Worker** `metar-to-iwxxm-worker`: `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` + poller **PRESENT** (keep).

### Agent 3 — Data / volumes

N/A — operator history is browser IndexedDB; no new Modal/volume assets.

### Agent 4 — Resources

PASS — image-based Render services; GHCR `main-latest` train (#786/#787/#788).

### Agent 5 — Template

PASS — `static+api+worker`; no Modal deploy template required.

### Agent 6 — Browser connectivity readiness

| Check | Status |
|-------|--------|
| `tests/unit/test_cors_policy.py` (H0c) | **PASS** 6/6 |
| `scripts/deploy/verify_connectivity.sh` | present |
| `tests/smoke/test_staging_connectivity.py` | present |
| Staging secrets / CORS matrix | PASS (`docs/ops/staging-secrets-matrix.md` + env-contract) |
| Live H4–H5 (T7.2) | **PASS** (prior); re-run at **13** |
| Live probes (this stage) | `/health` 200; `/auth/login` **404**; FE `/config.json` no `disableAuth`; form convert **200** w/o JWT |

## Pre-Deploy checklist

- [x] Configuration complete (no gaps)
- [x] Secrets cutover mostly done (`DISABLE_AUTH` / publishable gone); optional API `SUPABASE_*` cleanup at 13
- [x] Data assets N/A
- [x] Resource allocation verified (Render images)
- [x] Rollback plan reviewed (user approved)
- [x] H0c CORS unit tests pass
- [x] Frontend config ↔ API URL matrix (runtime `/config.json`)
- [x] CORS origins documented (`config/prod.json` / live config)
- [x] Post-deploy H4–H5 command documented (`make test-live-connectivity`)

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image / CI build failure | Wait for GHCR `main-latest` before redeploy | **approved** |
| 2 | Stale FE `/config.json` (`disableAuth`) | #787 omit bake; H5 asserts absent | **approved** |
| 3 | Auth secrets removed too early / leftover | Publishable/`DISABLE_AUTH` gone; optional API `SUPABASE_*` delete at 13 | **approved** (optional) |
| 4 | CORS / browser connectivity | `corsOrigins` + H0c + H4–H5 at 13 | **approved** |
| 5 | Rate-limit false positives | Defaults 60/10; env overrides available | **approved** |
| 6 | Dissemination allowlist empty | Fail-closed intentional; keep populated allowlist | **approved** |

**D-S023-12-mitigations:** User approved all (option 1); API `SUPABASE_*` optional at 13 (2026-07-28).

## Rollback

- Command: Redeploy previous Render deploy (API + FE) from dashboard, or revert merge commit on `main` and wait for GHCR rebuild
- Procedure:
  1. Identify last-known-good Render deploy IDs (API + FE)
  2. Redeploy those images (image-based — env-only changes need explicit redeploy)
  3. Re-run `make test-live-connectivity` (H4–H5)
  4. Auth-era rollback only if reverting pre-F21 image (would need Auth env restored)
- Last known good: F21 live train after #786/#787 (FE image `frontend:20260728202600-0a03c00`); tip docs `489c9bf`
- Source: `docs/deploy.md` §Rollback
- User review: **Approved** (D-S023-12-rollback, 2026-07-28)

## Live evidence (12)

```text
GET  /health              → 200
POST /auth/login          → 404
GET  FE /config.json      → 200; api.baseUrl OK; disableAuth absent
POST /api/v1/convert form → 200 (no JWT)
H0c                       → 6 passed
```

## Sign-Off

- [x] User approved implementation (11-verify-impl)
- [x] Deploy strategy verified (this checklist)
- [x] Ready for 13-deploy-smoke

## Summary

```
Deploy Strategy Verification Complete.

Pre-deploy checks:
  Configuration: PASS
  Secrets:       PASS (optional API SUPABASE_* cleanup → 13)
  Data/Volumes:  N/A
  Resources:     PASS
  Connectivity:  PASS (H0c + live probes; H4–H5 re-run at 13)

Failure mitigations: 6 risks approved
Rollback plan: reviewed and approved

Deploy gate:
  ✓ QA checks passed (09-qa)
  ✓ E2E behaviors passed (10-e2e)
  ✓ Implementation verified (11-verify-impl)
  ✓ Deploy strategy verified (12-verify-deploy)
  → Ready for 13-deploy-smoke

Next step: 13-deploy-smoke
```
