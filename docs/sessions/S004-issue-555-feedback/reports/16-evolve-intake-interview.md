# EV-004 Phase 0 — F5 work history interview (re-confirmation)

**Session**: S004-issue-555-feedback  
**Cycle**: EV-004  
**Date**: 2026-06-23  
**Stage**: 16-evolve Phase 0 intake

## Context

User requested interview on uncertainties for per-user METAR work history (Draft / WIP / Finished)
in Supabase, linked to auth, as part of [GitHub #555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555).

Prior delta requirements (2026-06-23) already documented F5 in `docs/feature-list.md`, `docs/spec.md`,
`docs/context/metar-work-history.md`. This session re-confirmed all decision points via structured
interview.

## Confirmed decisions

| Topic | Decision |
|-------|----------|
| History model | Snapshot list — one row per session with current status + full payload; no transition audit table in v1 |
| Granularity | One row = converter batch (manual textarea + file queue) |
| Statuses | Draft → WIP → Finished; Failed on convert error |
| Finished | Only after successful operational DB send; convert-only stays WIP |
| Guests | May convert without login; persistence requires auth |
| Login resume | Auto-resume most recent non-Finished, non-deleted session |
| Multi-session | Multiple Draft/Failed OK; max one WIP; New METAR for fresh Draft |
| Failed recovery | Stay Failed until user edits and re-converts |
| Send failure | Stay WIP — user retries send |
| Finished reopen | Read-only in v1 |
| Retention | Draft auto-purge 30d (pg_cron); soft-delete trash 30d restore |
| Admin | Read-only browse on separate admin page |
| API pattern | Backend REST + JWT; no direct browser Postgres writes |
| UI | Converter sidebar (5 recent) + My METARs page with filters |
| Multi-tab | Last-write-wins on auto-save |
| Cycle scope | Single EV-004 — #555 UX + F5 + S003 Supabase config |

## Outcome

All answers align with drafted spec. User approved proceed with EV-004 routing
(02-verify-plan → 04-tech-plan → build).

## Next stage

`01-requirements` (delta verification) → `02-verify-plan`
