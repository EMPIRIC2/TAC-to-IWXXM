# Execution plan — EV-007 / S010

**Cycle**: EV-007 — Issue #655 TAC traceability UX  
**Branch**: `evolve/EV-007-issue-655-tac-traceability`  
**Feature**: F6 delta (UI-only)

## Milestone M1 — Traceability UX

| Task | Description | Spec | Status |
|------|-------------|------|--------|
| T1.1 | `resultTraceability` util + unit tests | TC-001b | completed |
| T1.2 | `FileConverter` — resolve TAC, card header, always-on Source TAC | UJ-001 step 7 | completed |
| T1.3 | Vitest updates + new fallback test | TC-001b | completed |
| T1.4 | Playwright mocked Source TAC assertion | TC-001b | completed |
| T1.5 | Spec deltas (test-plan, journeys, feature-list) | Corpus | completed |

## Milestone M2 — Verify & deploy

| Task | Description | Status |
|------|-------------|--------|
| T2.1 | 08-verify-build (lint, tsc, vitest) | pending |
| T2.2 | 09-qa + 10-e2e | pending |
| T2.3 | 11-verify-impl (UJ-001 traceability AC) | pending |
| T2.4 | 12-verify-deploy + 13-deploy-smoke (frontend) | pending |

## PR plan

| PR | Title | Base |
|----|-------|------|
| PR-EV007 | `[EV-007] F6: TAC traceability UX (#655)` | `main` |
