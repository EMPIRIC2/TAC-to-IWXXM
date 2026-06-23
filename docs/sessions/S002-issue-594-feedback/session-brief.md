# Session S002 — Issue #594 Testing Feedback

| Field | Value |
|-------|-------|
| **Session ID** | S002-issue-594-feedback |
| **Type** | hotfix + feature (bundled) |
| **Status** | in_progress |
| **Branch** | `fix/S002-issue-594-feedback` (proposed) |
| **Started** | 2026-06-22 |
| **Orchestrator** | 14-hotfix (COR) → 16-evolve (traceability) |

## Intent

Address follow-up tester feedback in [GitHub #594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594):

1. **COR handling** — METAR/SPECI with correction indicator produce `translationFailedTAC`.
2. **Input traceability** — show original TAC per converted result, not only `manual_input`.
3. **`=` terminator** — reporter notes resolved; monitor only.

Parent feedback: [#555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555). Recent UI: [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656) / S001.

## Scoped context

- [docs/context/issue-594-feedback.md](../../context/issue-594-feedback.md)

## Resolutions (from 00-context)

| ID | Decision |
|----|----------|
| R2 | GIFTs decoder TPG grammar fix (COR-after-time); no backend preprocessor |
| R3 | `tac_input` on API + TAC display in UI |
| R4 | #594 only — exclude #555 deferred items |

## Out of scope

- Auto-clear input panel, in-app error log preview (#555).
- Migration / monorepo structural work (REQ-016).
