# BUG-2026-06-24 — Production login fails: "Legacy API keys are disabled"

| Field | Value |
|-------|-------|
| Status | `resolved` |
| Severity | Critical (production login fully blocked) |
| Feature | M4 (auth merged into backend) / F5 (work history requires login) |
| Reported | 2026-06-24 |
| Environment | Production only (Render API + Supabase `ktvxijislbtgqapllmuk`) |
| Remediation path | config rotation (Render) + code hardening |
| Related | S003-supabase-keys-config (paused), ADR-010, BUG-2026-06-23-supabase-service-key-leak |

## Error description

After **legacy Supabase API keys were disabled** in the Supabase dashboard, every production
login attempt fails. The browser console shows the backend returning `401` and the message
`Authentication failed: Legacy API keys are disabled`. No users can log in.

## Error logs

```
App-DF8v4ahQ.js:187 [Auth Service] Initialized with URL: https://metar-to-iwxxm-api.onrender.com
App-DF8v4ahQ.js:187 [Auth Service] Logging in user: Object
App-DF8v4ahQ.js:187 [Auth Service] Login response status: 401
installHook.js:1 [Auth Service] Login error: Object
installHook.js:1 [Auth Service] Login exception: Error: Authentication failed: Legacy API keys are disabled
    at Oc (App-DF8v4ahQ.js:187:171399)
    at async u (App-DF8v4ahQ.js:188:28498)
    at async App-DF8v4ahQ.js:188:23982
installHook.js:1 Login error: Error: Authentication failed: Legacy API keys are disabled
```

## Investigation

| Step | Finding |
|------|---------|
| Wrapper origin | `Authentication failed: {str(e)}` is added by `SupabaseAuthProxy.sign_in` (`packages/auth/src/supabase_proxy.py:141`) |
| Inner message | `Legacy API keys are disabled` is returned by Supabase GoTrue when the request `apikey` is a legacy `anon`/`service_role` JWT and legacy keys are disabled |
| Key resolution | `SupabaseAuthProxy.__init__` calls `get_supabase_publishable_key()` (`packages/shared/src/metar_shared/supabase_env.py:35`) |
| Fallback shim | `_resolve_with_fallback` returns `SUPABASE_PUBLISHABLE_KEY` if set, else **silently falls back** to legacy `SUPABASE_ANON_KEY` |
| Conclusion | Deployed Render API has no (valid) `SUPABASE_PUBLISHABLE_KEY` → falls back to legacy `SUPABASE_ANON_KEY` (now disabled) → Supabase rejects |
| Timeline | User confirms failure began immediately after disabling legacy keys in Supabase dashboard |
| Render evidence (2026-06-24) | API service `srv-d69v688gjchc73cn9kg0` had `SUPABASE_ANON_KEY` (JWT) only — no `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`, or `METAR_CONFIG_ENV` |
| Fix applied (config) | Set `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`, `METAR_CONFIG_ENV=prod` on Render API; deploy `dep-d8u5f83eo5us73dipdsg` → `live` |
| Post-fix probe | `POST /auth/login` → HTTP 200, session returned (admin@metar.local) |

**Root cause:** Config/secret drift. The deployed Render API service was still
authenticating to Supabase with a legacy `anon` JWT key (via the deprecation fallback shim)
because the canonical `SUPABASE_PUBLISHABLE_KEY` (`sb_publishable_*`) was not set there. Once
legacy keys were disabled in Supabase, the call started failing. The application code already
supported the new publishable key; no code change was required for the primary fix.

## Fix

### Config (deployed 2026-06-24)

Render API (`metar-to-iwxxm-api`) env vars added/updated from local `.env`:

- `SUPABASE_PUBLISHABLE_KEY` → `sb_publishable_*`
- `SUPABASE_SECRET_KEY` → `sb_secret_*`
- `DATABASE_URL`
- `METAR_CONFIG_ENV=prod`

Deploy triggered and reached `live`.

### Code hardening (local, pending PR)

- `packages/shared/src/metar_shared/supabase_env.py` — refuse legacy JWT anon fallback in production
- `packages/auth/src/supabase_proxy.py` — actionable `ValueError` when prod is misconfigured
- `packages/auth/src/admin_api.py` — `/admin/pending-users`, `/admin/approve-user`, `/admin/reject-user` (UserApprovalPanel no longer uses browser Supabase client)
- `apps/frontend/src/app/components/admin/UserApprovalPanel.tsx` — fetch merged API admin routes
- `apps/backend/src/services/work_session_service.py` — 503 + migration hint when `metar_work_sessions` table missing
- `tests/bugs/test_bug_2026_06_24_login_legacy_api_keys_disabled.py` — regression tests (3/3 pass)
- `tests/bugs/test_bug_2026_06_24_admin_pending_users_legacy_supabase.py` — UserApprovalPanel must not import Supabase client

## Spec conformance

| Check | Result |
|-------|--------|
| `docs/env-contract.md` §Production | Render API must set `SUPABASE_PUBLISHABLE_KEY` (`sync: false`); "Disable legacy JWT keys after migration" — disabled before Render rotation completed |
| ADR-010 | Publishable/Secret keys canonical; legacy shim is one-release only — fallback is now actively harmful |
| `feature-list.md` M4 | Auth on backend host — in scope |

## Repro test

`tests/bugs/test_bug_2026_06_24_login_legacy_api_keys_disabled.py`

| Test | Status |
|------|--------|
| `test_prod_does_not_use_legacy_jwt_anon_fallback` | green (after hardening) |
| `test_local_still_allows_legacy_jwt_anon_fallback` | green |
| `test_supabase_proxy_rejects_legacy_jwt_in_prod` | green |

Production config repro: Render API had only `SUPABASE_ANON_KEY` (JWT) — confirmed via Render API.

## Verification plan

| Layer | Check | Status |
|-------|-------|--------|
| L1 | Bug repro tests + related unit tests | pass (33/33) |
| L2 | `POST /auth/login` on production API | pass (HTTP 200) |
| L3 | Pre-deploy smoke | skip (config-only deploy) |
| L4 | User confirms browser login on production frontend | pass (user confirmed 2026-06-24) |

## Prevention & countermeasures

| Question | Answer |
|----------|--------|
| Recurrence risk | Possible on similar config changes |
| Automated guards | Bug repro test (done) + strengthen `make env-check` for `sb_publishable_*` in prod |

**Planned actions**

- Done: `tests/bugs/test_bug_2026_06_24_login_legacy_api_keys_disabled.py` + prod JWT fallback refusal in `supabase_env.py`
- Follow-up: implement `scripts/env/verify-sync.sh` Render key format check (S003 T9 backlog)

## Follow-ups

| Item | Status |
|------|--------|
| Code hardening committed + PR #689 (CI green) | done |
| Remove stale `SUPABASE_ANON_KEY` from Render API env | done (HTTP 204) |
| GitHub secrets updated (`FRONTEND_VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`, `FRONTEND_VITE_SUPABASE_URL`) | done |
| Frontend `/config.json` still bakes legacy JWT (image built in CI) — rebuilds with new key automatically on next `main` push (PR #689 merge) | pending merge |
| Rotate the Render API key exposed in chat | **pending (user)** |
| **Post-login (2026-06-24):** `UserApprovalPanel` queried `user_profiles` via browser Supabase client → "Legacy API keys are disabled" on pending users | **fixed in branch** — route through `/admin/pending-users`, `/admin/approve-user`, `/admin/reject-user` |
| **Post-login (2026-06-24):** `[App] work session init failed: Work session database error` | **likely** migration `20250623000007_metar_work_sessions.sql` not applied on production Supabase — operator must `supabase db push`; code now returns 503 with migration hint |

**Note:** The live frontend is image-based (`ghcr.io/.../frontend:main-latest`); its
`config.json` publishable key is baked at CI build time from
`FRONTEND_VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`. Render env vars on the static service do
not affect it. Merging PR #689 to `main` triggers the frontend image rebuild + Render
redeploy with the corrected key.
