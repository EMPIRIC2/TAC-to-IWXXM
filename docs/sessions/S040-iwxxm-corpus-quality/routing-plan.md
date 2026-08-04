# Routing plan — S040-iwxxm-corpus-quality

**Preset:** Standard — approved `D-S040-route` = 1  
**Orchestrator:** 16-evolve · **Cycle:** EV-032  
**Path:** `00→16→01→02→04→07→08→09→10→11→12→13`  
**Skip:** `03, 05, 06` (re-add if 04 introduces new deps/ADR tooling/guardrails)  
**Work order:** #835 → #741 (F32) → #808 → corpus children under #846  
**Exclude:** #836 metrics UI  
**Branch:** `evolve/EV-032-iwxxm-corpus-quality` from `main` (`D-S040-branch` = 1)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Intake + route + branch approved |
| 16-evolve | yes | orchestrator | **in_progress** | Phase A done; Phase B → 04 |
| 01-requirements | yes | delta | **completed** | Full pack + F7 VONA (`D-S040-E32-M`=2,3,1,1) |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS (`D-S040-02-phase-a`=1); Batch F `1,1,1,1` |
| 03-plan-tooling | no | — | skipped | Re-add if new rules/hooks |
| 04-tech-plan | yes | delta | **in_progress** | Gate B → execution plan |
| 05-verify-tech | no | — | skipped | Re-add if new deps |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | pending | Order: #835 → #741 → #808 → corpus |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | yes | delta | pending | — |
| 10-e2e | yes | smoke | pending | H4–H5 only if FE/catalog ships |
| 11-verify-impl | yes | delta | pending | Per-Fn (F32 + deepen) |
| 12-verify-deploy | yes | delta | pending | — |
| 13-deploy-smoke | yes | full | pending | — |

## Skip rationale

Existing app; engine + docs quality. Standard matches S037 quality residual pattern.
No new deployable. UI preview default **docs/repo** unless VONA/catalog forces FE.

Lean would skip 04/07/08/09/11/12 — insufficient for F32 encode + ADR-032 equality.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open / Phase 0 | `D-S040-open` = **1,1,1,1** — Epic #846; full scope; F32; order #835→#741→#808→corpus | 2026-08-04 |
| Routing | `D-S040-route` = **1** — Standard approved | 2026-08-04 |
| Branch | `D-S040-branch` = **1** — cut from `main` | 2026-08-04 |
| Document Manifest | `D-S040-E32-M` = **2,3,1,1** — full pack; full F7 VONA; no interview UI preview; → 02 | 2026-08-04 |
| Batch F (02) | `D-S040-02-batch-f` = **1,1,1,1** — AHL→04; incremental Examples; #808 docs+#847 | 2026-08-04 |
| Gate A | `D-S040-02-phase-a` = **1** — PASS → **04-tech-plan** | 2026-08-04 |
