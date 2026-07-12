---
session_id: S004-issue-555-feedback
type: feature
status: in_progress
branch: feat/S004-issue-555-feedback
started_at: 2026-06-23
intent: "EV-004: #555 UX + F5 Supabase work history + S003 config"
orchestrator: 16-evolve
evolve_cycle_id: EV-004
context_briefs:
  - docs/context/issue-555-feedback.md
  - docs/context/metar-work-history.md
standing_docs_touched:
  - docs/decisions/evolve-decisions.md
  - docs/feature-list.md
  - docs/decisions/requirements-decisions.md
github_issue: https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555
supersedes_session: S003-supabase-keys-config
---

# Session S004 — EV-004 (#555 + F5 + S003)

## Intent

Close remaining [GitHub #555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555) UX gaps **and**
deliver **F5** per-user METAR work history in Supabase, including **S003** Supabase config fixes as a prerequisite.

## Scope

**In scope**

- **F1 / #555** — Replace (not append) result cards; in-app error log from API `errors`/`issues`.
- **F5** — `metar_work_sessions` table, RLS, backend REST, Draft→WIP→Finished+Failed lifecycle, auto-save, resume-on-login, sidebar (5) + My METARs, admin read-only.
- **S003** — Supabase service-key leak fix + runtime config wiring.

**Out of scope**

- S001 buttons / send feedback (done).
- Admin mutate other users' sessions.
- KV upload backfill into F5.

## Key decisions (2026-06-23 interview)

| Topic | Decision |
|-------|----------|
| Cycle | Single EV-004 — merged scope |
| Statuses | Draft, WIP, Finished, Failed |
| Auth | Login required for all persistence |
| Granularity | One row = manual + file queue batch |
| Re-convert | Replace UI + overwrite session row |
| Resume | Most recent non-Finished on login |
| Finished | Only after successful DB send |
| Retention | Draft 30d auto-purge; soft-delete trash 30d |

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- [evolve-decisions.md §EV-004](../../decisions/evolve-decisions.md)
- [metar-work-history.md](../../context/metar-work-history.md)
- [issue-555-feedback.md](../../context/issue-555-feedback.md)
