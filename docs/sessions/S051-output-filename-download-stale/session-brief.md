# Session brief — S051-output-filename-download-stale

| Field | Value |
|-------|-------|
| **Type** | hotfix |
| **Intent** | Fix #904 — after convert, Output filename field changes must apply to Download / ZIP member names (BUG-2026-08-07-output-filename-download-stale) |
| **Branch** | `fix/output-filename-download-stale` (merged via PR #905 @ `a15541e5`) |
| **Orchestrator** | 14-hotfix |
| **Bug report** | [docs/bug-reports/BUG-2026-08-07-output-filename-download-stale.md](../../bug-reports/BUG-2026-08-07-output-filename-download-stale.md) |
| **GitHub** | [#904](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/904) (closed) |
| **PR** | [#905](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/905) (merged) |
| **Remediation** | local-first; Deploy landed with main CI after merge |
| **Started** | 2026-08-07 |
| **Status** | Phase 5 complete — pending close AskQuestion + closeout commit |

## Routing

1. `14-hotfix` — full (**Phase 5 done**; close pending)
2. `15-service-health` — optional (not requested)

## Notes

Opened after S050/EV-042 close. Origin feature: #664 (custom output filename).
Cursor rule: `.cursor/rules/optional/workbench-live-output-filename-download.mdc`.
Follow-up next PR: shared download-name path + F1/F10 journeys/product note.
