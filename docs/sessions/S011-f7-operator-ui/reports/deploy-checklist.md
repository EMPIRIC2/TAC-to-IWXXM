# Deploy Checklist — S011 M6 / T6.4 (12-verify-deploy)

> **Generated**: 2026-07-14  
> **Skill**: 12-verify-deploy (delta — EV-008 / F7)  
> **Session**: S011-f7-operator-ui / EV-008  
> **Branch tip**: `a8539f0` on `evolve/S011-f7-operator-ui` (**44 commits** ahead of `main`)  
> **User approval**: **Approved** 2026-07-14 — option 1 (`D-S011-EV008-deploy-check-A`)  
> Next: commit artifacts → PR-EV-008 → **merge/deploy still requires explicit approval**

## Target topology (unchanged)

| Role | Render service | URL |
|------|----------------|-----|
| API | `metar-to-iwxxm-api` | https://metar-to-iwxxm-api.onrender.com |
| Frontend | `metar-to-iwxxm-frontend-v4-web` | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Worker | `metar-to-iwxxm-worker` | untouched this cycle |

Deploy mode: **image** (`RENDER_DEPLOY_MODE=image` in `ci-cd.yml`) → GHCR `main-latest` + Render deploy hooks on **main** push.

## Pre-deploy checks

| Area | Status | Evidence |
|------|--------|----------|
| Config / Blueprint | PASS | `render.yaml` API + frontend-v4-web + worker; `METAR_CONFIG_ENV=prod` |
| Secrets on API | PASS | `SUPABASE_*`, `DATABASE_URL`, `METAR_CORS_ORIGINS` present (dashboard) |
| CORS ↔ frontend | PASS | Live `METAR_CORS_ORIGINS` / `FRONTEND_URL` = frontend-v4-web URL |
| Live health (current prod) | PASS | API `/health` 200; frontend `/config.json` 200 with matching `api.baseUrl` |
| H0c | PASS | `pytest tests/unit/test_cors_policy.py` — 6 passed |
| Connectivity scripts | PASS | `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` present |
| F7 migration | PASS | `20260714000010_tac_work_sessions` already applied remotely (13 rows) |
| 11-verify-impl | PASS | F7 approved with waivers (`verify-impl.md`) |
| Tip on `main` | **FAIL / blocker** | Evolve tip not merged; prod still pre-F7 (last API live deploy ~2026-07-13) |
| Uncommitted T6.2 fix | **WARN** | QA-001 `api.py` + session reports uncommitted |
| Local Playwright / compose | SKIPPED | Host ports/disk (deferred to post-deploy / CI) |
| Worker | N/A | No F7 worker change |

## Failure modes & mitigations

| Risk | Mitigation |
|------|------------|
| Deploy image without F7 commits | Merge `evolve/S011-f7-operator-ui` → `main` (PR-EV-008) before CI image build |
| Soft-preview type narrow missing in image | Commit QA-001 before merge |
| CORS regression | Re-run `make test-live-connectivity` after frontend rebuild |
| Session API vs old `metar_work_sessions` clients | Migration already cut over; clients must send `product` |
| Rollback | Redeploy prior Render deploy / previous GHCR tag from dashboard |
| Disk full on agent host | Deploy via Render/CI, not local docker build |

## Recommended deploy sequence (T6.4 → 13)

1. Commit QA-001 + `qa-report` / `e2e-report` / `verify-impl` / `deploy-checklist` (+ plan sync).  
2. Open or refresh **PR-EV-008** (`evolve/S011-f7-operator-ui` → `main`); ensure CI green.  
3. Merge with explicit user approval.  
4. Confirm `ci-cd.yml` push builds GHCR images + Render hooks (API then frontend).  
5. Run 13 smokes: H1–H3 API → `verify_connectivity.sh` (H4–H5) → optional H6′ F7.

## Connectivity readiness (Agent 6)

| Item | Ready for 13? |
|------|---------------|
| H0c | Yes |
| `METAR_CORS_ORIGINS` includes prod frontend | Yes (live) |
| `/config.json` `api.baseUrl` → API | Yes (live prod; rebuild after F7 merge) |
| `verify_connectivity.sh` | Yes — run post-deploy |
| H4–H5 now | No — run in 13 after F7 lands |

## Checklist signoff

- [x] User approves deploy strategy (merge → image → smokes) — D-S011-EV008-deploy-check-A
- [x] QA-001 + reports committed — `e86be26` (+ `1363a89`)
- [x] PR-EV-008 open — #716 (await CI green)
- [ ] Explicit merge + deploy approval for 13

**Recommendation:** Commit + prepare evolve→main PR; do not merge or Redeploy until user approves.
