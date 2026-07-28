# Deploy Smoke — S023 / EV-017 (F21 / F22 / #783)

> Date: 2026-07-28  
> Mode: **Validate existing** (no redeploy)  
> Status: **SMOKE PASS** — pending user sign-off  
> Branch tip: evolve docs `52c14e9`+; live GHCR `main-latest` (post #786/#787)

## Pre-Deploy

- Checklist: READY (`reports/deploy-checklist.md`)
- Decision: D-S023-13-validate-existing (user option 1)

## Deployment (existing)

| Field | Value |
|-------|-------|
| API | https://metar-to-iwxxm-api.onrender.com |
| FE | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API deploy | `dep-d9khddad0e5s73dmm4r0` (live) |
| FE deploy | `dep-d9khdedbedkc73aodib0` (live) |
| Images | `backend:main-latest` · `frontend:main-latest` |

## Smoke Tests

| Test | Status | Notes |
|------|--------|-------|
| H0c CORS unit | **PASS** | 6/6 |
| H1 `/health` | **PASS** | 200 (~241ms) |
| H3 convert (no JWT) | **PASS** | form convert 200; successful=1 |
| H3 live_api suite | **PASS** | 13 passed, 8 skipped (Auth-era login fixtures — expected F21) |
| H4 CORS preflight | **PASS** | 2/2 `test_staging_connectivity` |
| H5 `/config.json` | **PASS** | baseUrl match; `disableAuth` absent |
| Live Playwright F21/F22 | **PASS** | 5/5 after locator fix |
| TC-F21 `/auth/login` | **PASS** | 404 |
| Resources | **PASS** | No crash loop; services live |

### Fix during 13

- `apps/e2e/public-app-f21-f22.e2e.spec.ts` — use exact footer aria-label `Open privacy settings` (avoid strict-mode clash with notice button). Live TC-F22-003 green after fix.

## Optional cleanup (pending user)

| Item | Status |
|------|--------|
| API `SUPABASE_URL` / `SUPABASE_SECRET_KEY` | Still PRESENT — unused by public router; worker has own keys |

## Health Check

- `/health` healthy; `tac2iwxxm_available: true`
- Auth routes gone
- Error rate: acceptable (smokes green)

## Rollback

- Redeploy prior Render deploys or revert `main` (see deploy-checklist)
- Last known good: current live train post-#786/#787

## Changelog

- Session entry pending close (see `docs/CHANGELOG.md` S023)

## Sign-Off

- [ ] User approved smoke results
- [ ] Optional API `SUPABASE_*` cleanup: do / skip
- [ ] Stage 13 complete → evolve close
