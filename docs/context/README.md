# Scoped Context Briefs

Feature- and workflow-specific context gathered via **00-context scoped mode**. These files
supplement (never replace) the project-level `docs/context-brief.md` when one exists.

**Sessions:** Scoped briefs are linked from `docs/sessions/SNNN-slug/session-brief.md` when
part of an active pipeline session. See [sessions/README.md](../sessions/README.md).

| Slug | Topic | Status | Created | Linked features |
|------|-------|--------|---------|-----------------|
| [convert-send-buttons](convert-send-buttons.md) | Convert & Convert&Send UI (GitHub #656) | active | 2026-06-22 | F1, UJ-001 |
| [live-e2e-integration](live-e2e-integration.md) | Live E2E and integration tests for Render | requirements-complete | 2026-06-22 | test-plan H3–H6, UJ-001–003 |
| [issue-594-feedback](issue-594-feedback.md) | COR handling + input traceability (GitHub #594) | active | 2026-06-22 | F1 |
| [supabase-keys-config](supabase-keys-config.md) | Supabase secret keys, minimal env, Render↔Supabase↔local sync, advisor remediation | active | 2026-06-23 | F3, M4 |
| [issue-555-feedback](issue-555-feedback.md) | Initial test UX — auto-clear inputs/results, error log preview (GitHub #555) | active | 2026-06-23 | F1, UJ-001 |
| [metar-work-history](metar-work-history.md) | User METAR work sessions Draft→WIP→Finished in Supabase (F5) | active | 2026-06-23 | F5, F1, M4 |
| [issue-671-docker-db](issue-671-docker-db.md) | Docker Compose backend cannot create DB tables — localhost:5432 connect refused (GitHub #671) | active | 2026-06-25 | M1, docker-compose |
| [issue-664-output-filename](issue-664-output-filename.md) | Custom output filename for manual METAR input (GitHub #664) | active | 2026-06-25 | F1, UJ-001 |
| [general-tac-iwxxm-converter](general-tac-iwxxm-converter.md) | Generalizable C/Cython TAC→IWXXM + IWXXM-US architecture | active | 2026-07-12 | F1, F2, F4, proposed Fn |
| [realtime-tac-ingest](realtime-tac-ingest.md) | Near-RT ingest design + `iwxxm-validate` / `tac-validate` packages; F7/F8 Planned | active | 2026-07-12 | F2, F6, F7, F8 |

**Convention**: One brief per topic at `docs/context/<slug>.md`. Reference downstream as
`[Context: <slug> R#]`.
