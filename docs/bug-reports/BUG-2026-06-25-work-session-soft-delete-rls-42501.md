# BUG-2026-06-25 — Work-session soft-delete 502 (RLS 42501)

| Field | Value |
|-------|-------|
| **Status** | resolved (migration applied to prod; live-verified) |
| **Feature** | F5 (METAR work history) |
| **Severity** | medium — soft-delete + include_deleted/restore-of-deleted broken; create/update/list work |
| **Classification** | data / infra — Supabase RLS (SELECT policy enforced as UPDATE WITH CHECK) |
| **Remediation path** | Supabase RLS migration `20250625000008_metar_work_sessions_softdelete_rls.sql` |

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

## Investigation

### Confirmed root cause

The live policies (queried via `pg_policy`) match the repo migration — the UPDATE
policy `WITH CHECK` is just `auth.uid() = user_id`, which a soft-delete satisfies.
The blocker is the **SELECT** policy:

```sql
metar_work_sessions_select_own  FOR SELECT  USING (deleted_at IS NULL AND (auth.uid()=user_id OR is_admin()))
```

PostgreSQL **enforces a SELECT policy's `USING` as an implicit `WITH CHECK` on
UPDATE** (a row may not be updated into a state the caller can no longer see).
Setting `deleted_at` to a non-null value makes the new row fail `deleted_at IS
NULL`, so the UPDATE is rejected with `42501`.

Verified with a rolled-back SQL experiment impersonating the owner
(`SET LOCAL role authenticated` + `request.jwt.claims`):

| Test | Result |
|------|--------|
| `UPDATE … SET manual_tac` | OK |
| `UPDATE … SET deleted_at = now()` | **42501** (new row violates RLS) |
| same, after `ALTER POLICY …_select_own USING(owner-only)` | **OK** |

Also affected: `include_deleted=true` listing and getting/restoring already-deleted
rows — the SELECT policy hid them from owners.

### Fix

Migration `supabase/migrations/20250625000008_metar_work_sessions_softdelete_rls.sql`
relaxes the SELECT policy to ownership-only
(`auth.uid()=user_id OR is_admin()`), dropping the `deleted_at IS NULL` clause.
`deleted_at` filtering already happens in the app/query layer
(`WorkSessionService` applies `.is_("deleted_at","null")` unless `include_deleted`),
so visibility of deleted rows is not widened across users — only the owner/admin
can see their own soft-deleted rows (required for restore).

## Regression test

`tests/bugs/test_bug_2026_06_25_work_session_soft_delete_rls.py`:
- static: SELECT-policy `USING` in the fix migration must not reference `deleted_at` (CI guard).
- live (creds-gated): create → soft-delete (200) → restore (200) against the deployed API.

## Timeline

| When | Event |
|------|-------|
| 2026-06-25 | Found during auth hotfix live verification; documented as separate bug |
| 2026-06-25 | Root cause confirmed (SELECT-USING enforced as UPDATE WITH CHECK); migration + tests written |
| 2026-06-25 | Migration applied to prod; live-verified create 201 → soft-delete 200 → restore 200 |
