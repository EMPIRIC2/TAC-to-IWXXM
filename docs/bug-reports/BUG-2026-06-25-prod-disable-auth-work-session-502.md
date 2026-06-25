# BUG-2026-06-25 — F5 work-session persist 502 caused by prod auth bypass

| Field | Value |
|-------|-------|
| **Status** | resolved |
| **Feature** | F5 (METAR work history) + auth/security |
| **Severity** | high — F5 persist broken in production AND production running unauthenticated |
| **Classification** | config / infra (prod env) + code hardening (security) |
| **Remediation path** | config fix on Render (live) + local-first code hardening |

## Error description

Production F5 autosave fails after admin login. Browser console:

```
[useWorkSessionSync] persist failed: Error: Work session database error
```

This symptom was previously attributed to the supabase-py `.select()` chain
(BUG-2026-06-24, fixed by #690 / `a79c86e`). After that fix was confirmed
deployed, the symptom persisted — this report records the **actual** root cause.

## Error logs

Live API repro (2026-06-25, admin@metar.local):

```
POST /auth/login → 200
POST /api/v1/work-sessions → 502 {"detail":"Work session database error"}
```

Render app log (production) behind the 502:

```
[AUTH] verify_supabase_token disable_auth=True runtime_disable_auth=True has_credentials=True
Auth bypassed (development mode)
HTTP Request: POST .../rest/v1/metar_work_sessions "HTTP/2 400 Bad Request"
ERROR src.services.work_session_service: Work session database error
  File ".../work_session_service.py", line 162, in create_session
    response = self._client.table(TABLE).insert(data).execute()
postgrest.exceptions.APIError: {'message': 'invalid input syntax for type uuid: "dev-user-12345"', 'code': '22P02'}
```

## Investigation

### Verification the .select() fix was live (not the cause)

| Check | Result |
|-------|--------|
| Fix `a79c86e` on `main` | present — `.select()` removed from all mutations |
| ci-cd.yml on `main` (commit `9354c72`, incl. fix) | success → built/pushed `ghcr.io/.../backend:main-latest`, triggered Render deploy hook |
| Render `metar-to-iwxxm-api` (image-based) live deploy 13:54 | serving the fixed image |
| Real `create_session` locally vs prod Supabase (supabase-py 2.31, real admin JWT) | **201 / row** — code path is correct |
| Live API POST after fix deployed | still 502 → traceback shows **no** `.select()`/AttributeError |

### Root cause

The Render `metar-to-iwxxm-api` service had **`DISABLE_AUTH=true`** set (plus dev
placeholders `ADMIN_USER_ID=dev-user-12345`, `ADMIN_EMAIL=dev@example.com`).

`apps/backend/src/utilities/security.py` honoured this bypass unconditionally:

```python
if DISABLE_AUTH or disable_auth_runtime:
    admin_user_id = os.getenv("ADMIN_USER_ID", "dev-user-12345")
    return {"sub": admin_user_id, "authenticated": False, ...}
```

Consequences in production:

1. **Security**: auth was bypassed for **every** endpoint — production was
   effectively unauthenticated.
2. **F5 persist**: `create_work_session` used `sub = "dev-user-12345"` as
   `user_id`. PostgREST rejected the non-UUID value (`22P02`), which
   `_handle_db_error` mapped to the opaque 502 `Work session database error`.

The real authenticated path (auth enabled) resolves `sub` to the user's Supabase
UUID and forwards the JWT to PostgREST — verified to return 201.

### Spec conformance

| Check | Result |
|-------|--------|
| F5 api-contract POST /work-sessions → 201 | pass after fix |
| Security: prod must enforce auth | **drift** — prod ran with auth disabled (now fixed + guarded) |
| Blocking contradiction | none |

## Repro test

| Path | Status |
|------|--------|
| `tests/bugs/test_bug_2026_06_25_prod_auth_bypass_non_uuid.py` | RED before fix, GREEN after |

- `test_prod_does_not_bypass_auth_when_disable_auth_true_no_credentials` — prod + `DISABLE_AUTH=true`, no creds → 401 (was: dev bypass, no error).
- `test_prod_verifies_real_token_and_returns_uuid_subject` — prod + valid token → real UUID `sub`, `authenticated=True`.
- `test_non_prod_bypass_still_allowed` — local bypass preserved.

## Fix

1. **Production config (live, Render API):**
   - `DISABLE_AUTH` → `false`
   - removed `ADMIN_EMAIL` and `ADMIN_USER_ID` (dev placeholders)
   - triggered redeploy `dep-d8uje6ok1i2s73f1gvi0` (live 14:12)
2. **Code hardening (`security.py`):** `verify_supabase_token` ignores
   `DISABLE_AUTH` whenever `METAR_CONFIG_ENV` is `prod`/`production`, logging a
   warning and enforcing real auth. A stray bypass flag can never again silently
   disable production auth.

## Verification

| Layer | Check | Result |
|-------|-------|--------|
| L1 | ruff check / format, basedpyright, 13 security/bug tests | pass |
| L2 | Live POST /api/v1/work-sessions with valid JWT | **201**, `user_id=27f7a37c-…` |
| L2 | Live POST /api/v1/work-sessions with **no** token | **401** (auth enforced) |
| L4 | Render deploy live; auth enforced in prod | pass |

User to confirm in-browser (autosave indicator no longer `error`).

## Follow-ups

- **Soft-delete RLS (separate bug):** `DELETE /api/v1/work-sessions/{id}`
  (soft_delete sets `deleted_at` via UPDATE) returns 502 —
  `new row violates row-level security policy for table "metar_work_sessions"`
  (`42501`). Pre-existing; not the reported autosave symptom. Needs a Supabase
  RLS policy fix (UPDATE `WITH CHECK` allowing `deleted_at` to be set). File as
  its own bug.
- Confirm `DISABLE_AUTH` is not set on any other deployed service (frontend/auth).

## Timeline

| When | Event |
|------|-------|
| 2026-06-25 | Symptom re-reported after #690 deploy |
| 2026-06-25 | Confirmed `.select()` fix live; real cause = `DISABLE_AUTH=true` in prod (dev-user-12345 → 22P02) |
| 2026-06-25 | Render env fixed (DISABLE_AUTH=false, dev placeholders removed) + redeploy |
| 2026-06-25 | `security.py` hardened so prod ignores DISABLE_AUTH; regression tests added |
| 2026-06-25 | Live verify: create 201 (real UUID), unauthenticated 401 |
