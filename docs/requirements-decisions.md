# Requirements Decisions Log

> Stage: 01-requirements | Last updated: 2026-06-23

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| REQ-001 | Monorepo direction | Single git; reduce submodule complexity; preserve upstream pull for iwxxm | confirmed |
| REQ-002 | iwxxm-* upstream | Vendored snapshots from wmo-im; no git submodules for schemas | confirmed |
| REQ-003 | GIFTs placement | `packages/gifts` — full source; manual merge from mgoberfield when chosen | confirmed |
| REQ-004 | Auth shape | `packages/auth` library merged into backend; single deployable API | confirmed |
| REQ-005 | Workspace tooling | Makefile + uv workspace + pnpm workspaces | confirmed |
| REQ-006 | Migration approach | Big-bang — one PR removes all submodules | confirmed |
| REQ-007 | Target layout | `apps/{backend,frontend,e2e}` + `packages/{auth,gifts,shared}` + `vendor/schemas/*` | confirmed |
| REQ-008 | Legacy repos | Archive after stable deploy; monorepo sole active dev target | confirmed |
| REQ-009 | Vendor sync trigger | Scheduled GitHub Action opens PR on wmo-im new tags | confirmed |
| REQ-010 | Deploy topology | Two Render services — API (backend+auth) + static frontend | confirmed |
| REQ-011 | Big-bang scope | Structure + auth merge + docs + test reorganization | confirmed |
| REQ-012 | Shared package | `packages/shared` — types + cross-app utils | confirmed |
| REQ-013 | E2E location | `apps/e2e/` dedicated workspace | confirmed |
| REQ-015 | Vendor pinning | `vendor/manifest.json` — repo + tag/SHA per bundle | confirmed |
| REQ-016 | Non-goals | No product feature rewrites during migration | confirmed |
| REQ-014 | GIFTs sync | Manual merge from mgoberfield when chosen — no scheduled Action (audit 02-verify-plan) | confirmed |
| REQ-017 | Auth route prefix | `/auth/*` at API root after merge | confirmed |
| REQ-018 | Golden regression | TC-M003 normalized canonical XML diff | confirmed |
| REQ-019 | Legacy repo archive | After stable production deploy, not at merge | confirmed |
| REQ-020 | JS workspace | pnpm workspaces (frontend + packages/shared) | confirmed |

## Live E2E delta (2026-06-22)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| LIVE-001 | Scope | All tiers — H3 + H4–H5 + H6 full Playwright UJ-001–003 | confirmed |
| LIVE-002 | CI policy | Manual/local only — Makefile targets; no GitHub Actions live job | confirmed |
| LIVE-003 | Credentials | Local `.env` — `ADMIN_EMAIL` / `ADMIN_PASSWORD`; JWT at runtime via login | confirmed |
| LIVE-004 | Playwright scope | Full UJ-001–003 against Render (`DISABLE_AUTH=false`) | confirmed |
| LIVE-005 | Env naming | Canonical `LIVE_*` prefix; migrate away from `STAGING_*` / `E2E_*` | confirmed |
| LIVE-006 | URLs | API: `https://metar-to-iwxxm-api.onrender.com`; Frontend: `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | confirmed |
| LIVE-007 | Makefile | Individual targets + `test-live` umbrella | confirmed |
| LIVE-008 | Cold-start | Retry with backoff — 3 attempts, 30s wait | confirmed |
| LIVE-009 | Rate limits | Exponential backoff on HTTP 429 | confirmed |
| LIVE-010 | H3 coverage | Full suite — health, convert, validate, auth `/me` | confirmed |
| LIVE-011 | Stale tests | Fix/migrate `tests/test_playwright_e2e.py` to merged API | confirmed |
| LIVE-012 | Acceptance | Manual signoff before release — not a PR merge gate | confirmed |
| LIVE-013 | Prerequisite | E2E-001 schema path fix must land before live validate passes | confirmed |

## S003 — Supabase keys, config split, env sync (2026-06-23)

| ID | Topic | Decision | Status |
|----|-------|----------|--------|
| S003-R1 | Key naming | `SUPABASE_PUBLISHABLE_KEY` + `SUPABASE_SECRET_KEY` canonical; deprecate `ANON_KEY` / `SERVICE_ROLE_KEY` with shim | confirmed |
| S003-R2 | Frontend config | Runtime `/config.json` fetch at bootstrap; `config/prod.json` + publishable key inject at deploy | confirmed |
| S003-R3 | METAR project | `ktvxijislbtgqapllmuk`; migrations 003–004 **not yet applied** in production | confirmed |
| S003-R4 | Local ports | Standardize **18000** (frontend) / **18001** (API) everywhere | confirmed |
| S003-R5 | Secret key scope | `SUPABASE_SECRET_KEY` only for Auth Admin API (`create_admin_user.py`); admin routes use user JWT + RLS | confirmed |
| S003-R6 | Env sync | `env-contract.md` + `env-sync-runbook.md` + `make env-check`; align Render, Supabase, local, GitHub | confirmed |
| S003-R7 | Advisor scope | METAR tables only; CogniChem org projects out of scope | confirmed |
| S003-R8 | Auth dashboard | Enable leaked-password protection (HaveIBeenPwned) on METAR project | confirmed |
| S003-R9 | Config envs | `prod` + `local` only; `stage`/`dev` deferred | confirmed |

1. ~~Exact auth route prefix after merge~~ — resolved: `/auth/*` (REQ-017)
2. ~~pnpm vs npm~~ — resolved: pnpm (REQ-020)
3. ~~Golden file strategy for TC-M003~~ — resolved: normalized XML (REQ-018)
