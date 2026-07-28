# Routing plan — S024-dissemination-file-select

**Preset:** Lean+build (E18-3 amended by E18-7)  
**Orchestrator:** 16-evolve · **Cycle:** EV-018  
**Issue:** [#785](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/785)  
**Approval:** Phase 0 Batch 1+2 locked; scope-lock gate pending

| Stage | Required | Mode | Status | Skip rationale |
|-------|----------|------|--------|----------------|
| 00-context | yes | scoped | completed | Session open + scoped brief; Phase 0 locked |
| 16-evolve | yes | orchestrator | in_progress | EV-018 → 01 deltas written |
| 01-requirements | yes | delta | completed | Deepen F16 — `reports/01-requirements.md` |
| 02-verify-plan | yes | delta | completed | Phase A PASSED (D-S024-02-phase-a-A); M1/M2 → 04 — `reports/02-verify-plan.md` |
| 03-plan-tooling | **no** | — | skipped | No new Cursor rules/hooks expected |
| 04-tech-plan | yes | delta | completed | D-S024-04-plan-approve-A — plan approved; B→C; handoff 07 @ T1.1 |
| 05-verify-tech | **no** | — | skipped | Lean+build skip unless 04 adds deps/ADR conflict |
| 06-tech-tooling | **no** | — | skipped | No new tooling expected |
| 07-build | yes | full | completed | M1–M4 / 14 tasks done; tip a4b75f2; `reports/HANDOFF.md` |
| 08-verify-build | yes | full | in_progress | Lint / typecheck / full suite — STARTED after 07 |
| 09-qa | **no** | — | skipped | Lean+build; coverage via 08 + 10 |
| 10-e2e | yes | full | pending | Extend UJ-027–030 |
| 11-verify-impl | **no** | — | skipped | Lean+build |
| 12-verify-deploy | **no** | — | skipped | Lean+build; allowlist unchanged |
| 13-deploy-smoke | yes | full | pending | Live dissemination smoke when approved |

## Skip rationale

- **Lean+build (E18-7)**: `00→16→01→02→04→07→08→10→13` — skip 03/05/06/09/11/12.
- **E18-5**: N sequential `/preflight`+`/send`; UI aggregates (no batch API v1).
- **E18-6**: Selection count cap ≤20 + existing body/size limits.

## Approval

| Gate | Decision | Date |
|------|----------|------|
| Session open | **E18-1 A** | 2026-07-28 |
| Fn | **E18-2 B** deepen F16 | 2026-07-28 |
| Routing (initial) | **E18-3 B** Lean | 2026-07-28 |
| History sources | **E18-4 A** session+drops only | 2026-07-28 |
| API shape | **E18-5 A** N sequential | 2026-07-28 |
| Size caps | **E18-6 A** ≤20 + existing limits | 2026-07-28 |
| Routing amend | **E18-7 A** Lean+build | 2026-07-28 |
| UI preview | **E18-8 A** open local now | 2026-07-28 |
| Phase 0 scope lock | **D-S024-E18-scope-lock A** | 2026-07-28 |
| 01-requirements | deltas approved | 2026-07-28 |
| 02-verify-plan / Phase A | **D-S024-02-phase-a-A** | 2026-07-28 |
| 04 Batch 1 | **E18-9..12** / D-S024-04-E18-9..12 | 2026-07-28 |
| 04 Batch 2 | **E18-13..16** / D-S024-04-E18-13..16 | 2026-07-28 |
| 04 execution plan / Phase B→C | **D-S024-04-plan-approve-A** (option A) | 2026-07-28 |
| 07-build M1–M4 complete | 14/14 tasks; handoff 08 | 2026-07-28 |
