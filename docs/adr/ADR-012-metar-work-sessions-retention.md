# ADR-012: METAR Work Session Retention and pg_cron Jobs

## Status: Accepted

## Context

F5 requires:
- Hard-delete **Draft** rows where `updated_at < now() - 30 days`
- Soft-delete trash with **30-day restore**, then hard-delete
- At most **one WIP** session per user (non-deleted)

Supabase METAR project has pg_cron available (extension present per local catalog). Requirements
left the exact schedule expression open for 04-tech-plan.

## Decision

1. **Draft purge** — daily at `03:00 UTC` (`0 3 * * *`):
   ```sql
   DELETE FROM public.metar_work_sessions
   WHERE status = 'draft'
     AND deleted_at IS NULL
     AND updated_at < NOW() - INTERVAL '30 days';
   ```
2. **Trash hard-delete** — same cron job, second statement:
   ```sql
   DELETE FROM public.metar_work_sessions
   WHERE deleted_at IS NOT NULL
     AND deleted_at < NOW() - INTERVAL '30 days';
   ```
3. **WIP uniqueness** — partial unique index:
   ```sql
   CREATE UNIQUE INDEX metar_work_sessions_one_wip_per_user
   ON public.metar_work_sessions (user_id)
   WHERE status = 'wip' AND deleted_at IS NULL;
   ```
4. **Implementation** — migration `supabase/migrations/20250623000007_metar_work_sessions.sql`
   creates table, RLS policies, index, `purge_stale_metar_work_sessions()` function, and
   `cron.schedule('purge-metar-work-sessions', '0 3 * * *', $$SELECT public.purge_stale_metar_work_sessions()$$)`.
5. **Local dev** — migration is idempotent; `supabase db reset` applies cron; operators verify
   job in Supabase dashboard SQL editor on production.

## Consequences

- Predictable off-peak purge; no per-hour load.
- DB rejects second WIP insert/update with unique violation — backend maps to HTTP 409.
- Cron requires manual verification on METAR Supabase project (MCP not linked per ADR-010).

## Alternatives Considered

| Alternative | Rejected because |
|-------------|------------------|
| Hourly cron | Unnecessary churn for 30-day TTL |
| Backend scheduled job on Render | No worker deployable; ephemeral filesystem |
| App-only WIP check | Race under concurrent tabs (F5-R25 last-write-wins) |

## References

- [metar-work-history.md](../context/metar-work-history.md) — R12, R17
- [requirements-decisions.md §F5-R8, F5-R11](../decisions/requirements-decisions.md)
