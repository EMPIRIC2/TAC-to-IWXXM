# BUG-2026-06-25 — Work-session soft-delete 502 (RLS 42501)

| Field | Value |
|-------|-------|
| **Status** | investigating |
| **Feature** | F5 (METAR work history) |
| **Severity** | medium — soft-delete/restore broken; create/update/list work |
| **Classification** | data / infra — Supabase RLS policy (UPDATE `WITH CHECK`) |
| **Remediation path** | not started — needs Supabase RLS migration (separate from BUG-2026-06-25 auth) |

## Error description

`DELETE /api/v1/work-sessions/{id}` (soft-delete — UPDATE sets `deleted_at`)
returns 502 `Work session database error`. Discovered while verifying the auth
hotfix (BUG-2026-06-25-prod-disable-auth-work-session-502); create (201) and
update/PATCH (200) succeed for the same authenticated user.

## Error logs

Production (admin@metar.local, valid JWT), 2026-06-25:

```
POST   /api/v1/work-sessions        → 201
PATCH  /api/v1/work-sessions/{id}   → 200
DELETE /api/v1/work-sessions/{id}   → 502 {"detail":"Work session database error"}
```

Render app log:

```
File ".../work_session_service.py", line 190, in soft_delete
    .execute()
postgrest.exceptions.APIError: {'message': 'new row violates row-level security policy for table "metar_work_sessions"', 'code': '42501'}
```

## Symptoms & reproduction

| Field | Value |
|-------|-------|
| Symptom | 502 on soft-delete (and likely restore) |
| Where | Production Render (live API) |
| Frequency | Every soft-delete attempt |
| Repro | login → create → DELETE /api/v1/work-sessions/{id} |

## Investigation (initial)

`soft_delete` runs:

```python
self._client.table(TABLE).update({"deleted_at": now}).eq("id", str(session_id)).is_("deleted_at", "null").execute()
```

PostgREST returns `42501` — the row produced by the UPDATE fails the table's RLS
**`WITH CHECK`** expression. A hard `DELETE` via PostgREST with the same JWT
**succeeds**, which points at the UPDATE policy's `WITH CHECK` rejecting rows
where `deleted_at IS NOT NULL` (so setting `deleted_at` is blocked), rather than a
USING/visibility problem.

`restore_session` (sets `deleted_at = NULL`) likely has the inverse exposure and
should be checked in the same migration.

## Hypothesis / likely fix

Supabase RLS migration on `metar_work_sessions`: the UPDATE policy `WITH CHECK`
must permit the owner to set `deleted_at` (and clear it on restore), e.g. scope
`WITH CHECK` to `user_id = auth.uid()` without constraining `deleted_at`.

Owner check, current policy: see
`apps/frontend/supabase/migrations/*metar_work_sessions*.sql` and Supabase
dashboard → Authentication → Policies.

## Regression test (for fix session)

Live or PostgREST-level test: as owner, create → soft_delete → expect 200 with
`deleted_at` set → restore → expect 200 with `deleted_at` null.

## Timeline

| When | Event |
|------|-------|
| 2026-06-25 | Found during auth hotfix live verification; documented as separate bug |
