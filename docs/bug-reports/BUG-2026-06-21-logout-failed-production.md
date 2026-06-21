# BUG-2026-06-21-logout-failed-production

| Field | Value |
|-------|-------|
| **Status** | verifying |
| **Feature** | M4 (auth merged into backend API) |
| **Severity** | critical (user report) |
| **Classification** | code bug (implementation drift) |
| **Remediation path** | local-first — deploy after user approval |

## Error description

Production logout fails every time when user clicks logout. Browser console shows:

```
[Auth Service] Initialized with URL: https://metar-to-iwxxm-api.onrender.com
Logout failed:
```

Stack trace points at `signOutWithScope` → `fetch(authUrl('/logout'))` in bundled frontend (`index-CvXTTHz_.js`).

## Error logs

```
index-CvXTTHz_.js:217 [Auth Service] Initialized with URL: https://metar-to-iwxxm-api.onrender.com
installHook.js:1 Logout failed: 
overrideMethod @ installHook.js:1
Vp @ index-CvXTTHz_.js:216
await in Vp
ke @ index-CvXTTHz_.js:216
onClick @ index-CvXTTHz_.js:216
```

## Symptoms & reproduction

| Field | User answer |
|-------|-------------|
| Symptom | Error / crash — Logout failed in console |
| Where | Production Render |
| When | After last deploy |
| Frequency | Every time |
| Repro env | Neither yet — user has not re-tested locally |
| Severity | Critical — cannot log out |
| Evidence | Console stack trace only (no Network tab) |
| Tried | Nothing |

## Investigation

### Timeline

| When | Event |
|------|-------|
| 2026-06-21 | User reports logout failure in production via hotfix intake |
| 2026-06-21 | Preliminary code read: `signOutWithScope` POSTs without `Authorization` header; API requires Bearer token |

### Hypotheses

| # | Hypothesis | Result |
|---|------------|--------|
| H1 | `signOutWithScope` missing `Authorization: Bearer` header → API 401 | **Confirmed** — live POST returns 401; repro test RED |
| H2 | CORS blocks logout POST (similar to prior login bug) | **Open** — needs Network tab or curl probe |
| H3 | Expired/invalid token causes 401 | **Open** |
| H4 | Wrong logout URL path | **Unlikely** — `authUrl('/logout')` → `/auth/logout` per `apiBase.ts` |

### Root cause

`signOutWithScope` (`apps/frontend/src/utils/supabase/logout.ts`) POSTs to `/auth/logout` with `{ scope }` body but **no `Authorization: Bearer` header**. Backend requires token via `get_token_from_header` → 401 → frontend logs `Logout failed:` with empty `statusText`. Used by FileConverter and AdminDashboard scoped logout menus. `authService.logout()` correctly sends Bearer but is a separate code path (App.tsx simple logout).

## Spec conformance

| Spec | Section | Result |
|------|---------|--------|
| docs/api-contract.md | POST /auth/logout — Bearer on protected routes | pass (API enforces; client drift) |
| packages/auth/src/api_supabase.py | get_token_from_header on logout | pass |
| apps/frontend/src/utils/authService.ts | logout() sends Bearer | pass (reference impl) |
| apps/frontend/src/utils/supabase/logout.ts | signOutWithScope | **implementation drift** — no Authorization header |

No blocking spec contradiction.

## Repro test

| Path | Status |
|------|--------|
| `tests/bugs/test_bug_2026_06_21_logout_missing_auth_header.py` | GREEN (2026-06-21) |

## Fix

**Branch:** uncommitted (local working tree)

**Change:** `apps/frontend/src/utils/supabase/logout.ts` — import `getAccessToken`, send `Authorization: Bearer` on POST `/auth/logout`; early-return true when no token stored.

**Tests updated:** `apps/frontend/src/utils/supabase/logout.test.ts` — asserts Bearer header sent when token present.

### TDD iteration log

| # | Action | Result |
|---|--------|--------|
| 1 | `test_sign_out_with_scope_sends_bearer_token` — source lacks Authorization | FAIL (expected) |
| 1 | `test_auth_logout_requires_bearer_token` — API contract | PASS |
| 1 | Live probe: POST /auth/logout no auth → 401 | Confirms H1 |

## Verification plan

| Field | Choice |
|-------|--------|
| Success criterion | New repro/regression test passes in CI |
| Checks | Full main CI parity (local) + gh on main after merge |
| Monitoring | User watches production after deploy |

## Verification

### Layer 1 — Automated

- [x] Repro test red → green (2026-06-21)
- [x] `logout.test.ts` — 4 passed
- [x] FileConverter + AdminDashboard tests — 74 passed
- [ ] Full CI parity (local) — pending before PR

### Layer 2 — Reproduction

- [ ] User logout flow succeeds

### Layer 3 — Pre-deploy smoke

- [ ] pending

### Layer 4 — Production

- [ ] pending

## Interview record

Phase 0 intake completed 2026-06-21.
