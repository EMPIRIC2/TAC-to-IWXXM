# Session brief — S028-sigmet-multiline-split

| Field | Value |
|-------|-------|
| **Type** | hotfix |
| **Intent** | Hotfix BUG-2026-07-30 — SIGMET/AIRMET multi-line manual TAC incorrectly line-split → PARSE_ERROR unable to parse SIGMET header on WMO A6-1a-TS UI example |
| **Branch** | `fix/BUG-2026-07-30-sigmet-multiline-split` |
| **Orchestrator** | 14-hotfix |
| **Bug report** | [docs/bug-reports/BUG-2026-07-30-sigmet-multiline-split.md](../../bug-reports/BUG-2026-07-30-sigmet-multiline-split.md) |
| **Started** | 2026-07-30 |
| **Completed** | 2026-07-30 |
| **Status** | completed |
| **PR** | [#796](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/796) merged `17c93bd` |

## Routing

1. `00-context` — scoped (**completed**)
2. `14-hotfix` — full (**completed**)

## Close note

PR #796 merged `17c93bd`; main CI Deploy PASS; live API soft-preview PASS (posList+WEAKEN);
UI `production_verified` deferred (user moved to F9 decode deepen / S029).
