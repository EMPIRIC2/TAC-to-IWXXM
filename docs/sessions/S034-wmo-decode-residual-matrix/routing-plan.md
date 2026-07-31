# Routing plan — S034-wmo-decode-residual-matrix

**Preset:** Lean+build + **13 when behavior/UI ships** (**approved** D-S034-open=1,1,2,1)  
**Orchestrator:** 16-evolve · **Cycle:** EV-027  
**Path:** `00→16→01→02→04→07→08→10` (+ `13` if FE/decode UX ships)  
**Skip:** `03, 05, 06, 09, 11, 12`

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Phase 0 locked D-S034-open=1,1,2,1 |
| 16-evolve | yes | orchestrator | in_progress | Phase 0 done; 01 interview |
| 01-requirements | yes | delta | **completed** | E27-M/UJ/TC=1,1,1; D-S034-E27-E1 |
| 02-verify-plan | yes | delta | **completed** | PASS Batch F 1,2,1; Gate A → 04 |
| 04-tech-plan | yes | delta | in_progress | Inventory + residual matrix + CI tasks |
| 07-build | yes | full | pending | Matrix tests + decode fixes / allowlist |
| 08-verify-build | yes | delta | pending | Full suite green |
| 09-qa | no | — | skipped | 08+10 cover |
| 10-e2e | yes | smoke | pending | Catalog Vitest + residual matrix pytest |
| 11-verify-impl | no | — | skipped | Lean+build |
| 12-verify-deploy | no | — | skipped | — |
| 13-deploy-smoke | when ships | full | pending | H4–H5 if FE menu/decode chrome ships |

## Skip rationale

Quality / CI matrix deepen on existing F25 catalog + F9 decode — no new deployable, no new Fn.
Lean+build matches S031/S033. 03/05/06 unnecessary (no new rules/deps/tooling). 09/11/12
covered by 08+10 (+13 when operator-visible ships). Routine Lean checkpoints skipped unless
gate failure.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Cycle pick | #815 Lean+build (user `/16-evolve` option 1) | 2026-07-31 |
| Session open / Phase 0 | `D-S034-open` = **1,1,2,1** — scope + Lean+build + UI defer + triage fix/allowlist | 2026-07-31 |
| UI preview | **2** — defer until after build | 2026-07-31 |
| Residual triage | **1** — fix when cheap; else allowlist + child issue | 2026-07-31 |
