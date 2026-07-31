# Routing plan — S032-iwxxm-us-remarks-va

**Preset:** Lean+build + **13 when behavior ships** (**approved** E25-3=1)  
**Orchestrator:** 16-evolve · **Cycle:** EV-025  
**Path:** `00→16→01→02→04→07→08→10` (+ `13` if convert/validate ships)  
**Skip:** `03, 05, 06, 09, 12` (re-add if 04 introduces new deps/ADR tooling); **11** skipped (no UI)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Session open; Phase 0 locked E25-* |
| 16-evolve | yes | orchestrator | **in_progress** | EV-025 Gate B approved; 07 @ M0 |
| 01-requirements | yes | delta | **completed** | E25-E1 — report 01-requirements.md |
| 02-verify-plan | yes | delta | **completed** | PASS — Batch F 1,1,1; report 02-verify-plan-audit.md |
| 04-tech-plan | yes | delta | **completed** | E25-T*; Gate B=`1`; execution-plan approved |
| 07-build | yes | full | **in_progress** | @ T0.1 theme map |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | no | — | skipped | 08+10 cover |
| 10-e2e | yes | smoke | pending | Library + API convert/validate US + VA stem |
| 11-verify-impl | no | — | skipped | No UI (E25-ui=1) |
| 12-verify-deploy | no | — | skipped | — |
| 13-deploy-smoke | when ships | full | pending | If API image behavior changes |

## Skip rationale

Engine encode/lint/validate deepen on existing packages; dig already done in EV-024.
No new deployable / no new Fn. Dual lane is large but still delta-mode on F6.b + F23.
13 only when operator-visible convert/validate behavior ships.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | S032 / `evolve/EV-025-iwxxm-us-remarks-va` | 2026-07-31 |
| Intake | E25-1=1, E25-2=1, E25-3=1, E25-4→2+3 → **E25-4b=2** dual lane + **E25-4c=3** all ❌ US | 2026-07-31 |
| Routing | Lean+build + 13-when-ships | 2026-07-31 |
| UI | E25-ui=1 N/A | 2026-07-31 |
| Gate A / 02 | Batch F 1,1,1; `D-S032-02-phase-a` → 04 | 2026-07-31 |
| 04 Batch T | E25-T1..T6 = 1,1,2,1,3,1; T5 supersedes S02.M2 Gate C soft deferral | 2026-07-31 |
| Gate B / 04 | `1` — M0–M7 approved → 07 @ T0.1 (`D-S032-04-plan-approve`) | 2026-07-31 |
