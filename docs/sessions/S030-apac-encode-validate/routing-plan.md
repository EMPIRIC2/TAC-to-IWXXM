# Routing plan — S030-apac-encode-validate

**Preset:** Lean+build + **13 when behavior ships** (**approved** E23-3 / E23-4)  
**Orchestrator:** 16-evolve · **Cycle:** EV-023  
**Path:** `00→16→01→02→04→07→08→10` (+ `13` if convert/validate ships)  
**Skip:** `03, 05, 06, 09, 12` (re-add if 04 introduces new deps/ADR tooling); **11** optional

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Session open; Phase 0 locked |
| 16-evolve | yes | orchestrator | **in_progress** | EV-023 |
| 01-requirements | yes | delta | **completed** | E23-E1 — report 01-requirements.md |
| 02-verify-plan | yes | delta | **completed** | PASS Batch F 1,1,1; Gate A → 04 |
| 04-tech-plan | yes | delta | **completed** | E23-T1..T6 1,1,2,2,1,1; B→C |
| 07-build | yes | full | **in_progress** | M0 done; next T1.1 NSC fixtures |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | no | — | skipped | 08+10 cover |
| 10-e2e | yes | smoke | pending | Convert/validate smoke if API surface changes |
| 11-verify-impl | optional | — | pending | — |
| 12-verify-deploy | no | — | skipped | — |
| 13-deploy-smoke | when ships | full | pending | E23-4 — required if convert/validate behavior deploys |

## Skip rationale

Cross-cutting encode/lint/SCH deepen on existing packages; mining docs already promoted.
No new deployable / no new Fn. 13 included when API image behavior changes.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | S030 / `evolve/EV-023-apac-encode-validate` | 2026-07-30 |
| Intake | E23-1=A, E23-2=all ticket, E23-3=A, E23-4=B | 2026-07-30 |
| Routing | Lean+build + 13-when-ships approved | 2026-07-30 |
