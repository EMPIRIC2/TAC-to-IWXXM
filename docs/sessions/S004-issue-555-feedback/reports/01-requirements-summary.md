# 01-requirements — EV-004 summary

**Session**: S004-issue-555-feedback  
**Cycle**: EV-004  
**Date**: 2026-06-23  
**Features**: F1 (#555 UX), F5 (user METAR work history)

## Scope confirmed

Single evolve cycle delivering:

1. **#555 remaining UX (F1)** — Replace result cards on successful convert; collapsible error log panel.
2. **F5 work history** — Supabase `metar_work_sessions`, Draft → WIP → Finished + Failed, per-user RLS.
3. **S003** — Supabase key/config prerequisites merged into same cycle.

## Interview decisions (2026-06-23)

| Topic | Decision |
|-------|----------|
| History model | Current state on one row — no audit trail table in v1 |
| Guest users | Convert without login; no persistence until auth |
| Send failure | Stay WIP |
| Finished sessions | Read-only when opened |
| Multi-device | Last-write-wins |
| New session | Explicit **New METAR** button |
| Sidebar switch | Load session; WIP row unchanged |
| Login | Auto-resume most recent non-Finished session |
| Error log | In-app panel + persist on row |
| Retention | Draft 30d purge; trash 30d restore |
| Admin | Separate read-only admin page |
| Storage | No explicit cap in v1 |
| Results (#555) | Replace on successful convert only |

## Documents updated

- `docs/requirements-decisions.md` — F5-R21…R32, F1-R555-1/2
- `docs/feature-list.md` — F1 #555 UX, F5 limitations/UI
- `docs/spec.md` — F5 business rules
- `docs/api-contract.md` — send failure transition, guest note, admin UI
- `docs/user-journeys.md` — UJ-001, UJ-004
- `docs/evolve-decisions.md` — EV-004 R13–R22
- `docs/context/metar-work-history.md` — R22–R30

## Next step

**02-verify-plan** — consistency check against updated specs.
