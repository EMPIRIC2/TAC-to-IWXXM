# BUG-2026-06-24-work-session-persist-select-chain

| Field | Value |
|-------|-------|
| **Status** | fixing |
| **Feature** | F5 (METAR work history) |
| **Severity** | high (user report) |
| **Classification** | code bug — supabase-py API incompatibility |
| **Remediation path** | local-first — deploy after user approval |

## Error description

Production F5 autosave fails after login. Browser console:

```
[useWorkSessionSync] persist failed: Error: Work session database error
```

Login succeeds (200); admin dashboard loads; persist on work session create/update fails.

## Error logs

```
App-DpmWmUb_.js:187 [Auth Service] Login success for: admin@metar.local
installHook.js:1 [useWorkSessionSync] persist failed: Error: Work session database error
```

Production API repro (2026-06-25):

```
POST /auth/login → 200
POST /api/v1/work-sessions → 502 {"detail":"Work session database error"}
GET  /api/v1/work-sessions → 200 {"items":[],"total":0}
```

Direct PostgREST insert with same JWT → 201 (RLS OK).

## Symptoms & reproduction

| Field | User answer |
|-------|-------------|
| Symptom | Error — persist failed |
| Where | Production Render |
| When | Always since F5 deploy |
| Frequency | Every persist attempt |
| Repro env | Production (admin@metar.local) |
| Severity | High — F5 completely broken |
| Evidence | Frontend console; agent reproduced 502 on live API |

## Investigation

### Timeline

| When | Event |
|------|-------|
| 2026-06-24 | User reports `[useWorkSessionSync] persist failed` via hotfix |
| 2026-06-25 | Supabase SQL: table, RLS, FK, `is_admin()` present; impersonated insert OK |
| 2026-06-25 | Direct PostgREST insert with admin JWT → 201 |
| 2026-06-25 | `WorkSessionService.create_session` via supabase-py **2.28** → `AttributeError: ... no attribute 'select'` |
| 2026-06-25 | Same code via uv **2.31** → create OK; production 502 indicates older supabase-py on Render |

### Root cause

`apps/backend/src/services/work_session_service.py` chains `.select("*")` after `.insert()` / `.update()`.
In **supabase-py 2.28** (production), insert/update builders are `SyncQueryRequestBuilder` /
`SyncFilterRequestBuilder` **without** `.select()`. This raises `AttributeError`, caught by
`_handle_db_error` and returned as opaque **502** `"Work session database error"`.

`.insert(data).execute()` and `.update(data).eq(...).execute()` alone return full rows via
PostgREST `Prefer: return=representation` (verified against live Supabase).

### Spec conformance

| Check | Result |
|-------|--------|
| F5 api-contract POST /work-sessions | pass — spec expects 201 + body |
| ADR-011 Supabase JWT client | pass — pattern correct; chain API wrong for prod lib version |
| Blocking drift | none |

## Repro test

| Path | Status |
|------|--------|
| `tests/bugs/test_bug_2026_06_24_work_session_persist_select_chain.py` | RED before fix (502 / AttributeError path) |

## Fix

Remove `.select("*")` from insert/update/soft-delete/restore mutations; rely on `.execute()` return payload.

## Verification plan

| Criterion | Check |
|-----------|-------|
| Success | POST /api/v1/work-sessions → 201 on production after deploy |
| Layer 1 | pytest bugs + work_session unit/integration |
| Layer 2 | Admin login + autosave indicator not `error` |
| CI | local parity before PR |
