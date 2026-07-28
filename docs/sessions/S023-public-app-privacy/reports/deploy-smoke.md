# Deploy Smoke — S023 / EV-017 (F21 / F22 / #783)

> Date: 2026-07-28  
> Mode: **Validate existing** + optional API `SUPABASE_*` cleanup  
> Status: **COMPLETE** — user approved (option 2)  
> Branch tip: `7837cd1`+; live GHCR `main-latest` (post #786/#787)

## Pre-Deploy

- Checklist: READY (`reports/deploy-checklist.md`)
- Decision: D-S023-13-validate-existing (user option 1)
- Sign-off: D-S023-13-approve-cleanup (user option 2 — delete API SUPABASE_* + redeploy)

## Deployment

| Field | Value |
|-------|-------|
| API | https://metar-to-iwxxm-api.onrender.com |
| FE | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| API deploy (pre-cleanup) | `dep-d9khddad0e5s73dmm4r0` |
| API deploy (post-cleanup) | `dep-d9kii12jobas73fl4bi0` **live** |
| FE deploy | `dep-d9khdedbedkc73aodib0` |
| Images | `backend:main-latest` · `frontend:main-latest` |

## Smoke Tests

| Test | Status | Notes |
|------|--------|-------|
| H0c CORS unit | **PASS** | 6/6 |
| H1 `/health` | **PASS** | 200 (pre + post cleanup) |
| H3 convert (no JWT) | **PASS** | 200; successful=1 (pre + post) |
| H3 live_api suite | **PASS** | 13 passed, 8 skipped (Auth-era — expected) |
| H4 CORS preflight | **PASS** | 2/2 (pre + post cleanup) |
| H5 `/config.json` | **PASS** | baseUrl match; `disableAuth` absent |
| Live Playwright F21/F22 | **PASS** | 5/5 after locator fix |
| TC-F21 `/auth/login` | **PASS** | 404 |
| Resources | **PASS** | API redeploy live; no crash |

### Fix during 13

- `apps/e2e/public-app-f21-f22.e2e.spec.ts` — exact footer aria-label for Privacy settings.

### API secret cleanup (D-S023-13-approve-cleanup)

| Key | Result |
|-----|--------|
| `SUPABASE_URL` | **Deleted** from API |
| `SUPABASE_SECRET_KEY` | **Deleted** from API |
| Worker `SUPABASE_*` / poller | **Unchanged** (kept) |
| `DISSEMINATION_EGRESS_ALLOWLIST` | **Kept** |
| Redeploy | `dep-d9kii12jobas73fl4bi0` → live; health/convert/H4–H5 re-PASS |

## Health Check

- `/health` healthy; `tac2iwxxm_available: true`
- Auth routes gone
- Public convert works without JWT after env cleanup

## Rollback

- Redeploy prior Render deploys or revert `main` (see deploy-checklist)
- Last known good: `dep-d9kii12jobas73fl4bi0` (post-cleanup) / FE `dep-d9khdedbedkc73aodib0`

## Sign-Off

- [x] User approved smoke results
- [x] API `SUPABASE_*` cleanup done + redeploy verified
- [x] Stage 13 complete → evolve close
