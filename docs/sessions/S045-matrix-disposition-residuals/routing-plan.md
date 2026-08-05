# Routing plan — S045-matrix-disposition-residuals

**Preset:** Lean + 07/08 — **approved** (Q3=1)  
**Orchestrator:** 16-evolve · **Cycle:** EV-037  
**Path:** `00→16→01→02→07→08→11`  
**Skip:** `03, 04, 05, 06, 09, 10, 12, 13`  
**Branch:** `evolve/EV-037-matrix-disposition-residuals`  
**Features:** deepen **F2 / F6 / F32** only (no new Fn)  
**Status:** Phase C / 07-build in_progress — Gate A **PASS**

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | S045 open; Q1–Q4 locked |
| 16-evolve | yes | orchestrator | **in_progress** | Phase 0–1 intake done (G2=1); orchestrator remains; child 07 |
| 01-requirements | yes | delta | **completed** | AC=1 approve AC1–AC4 |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS; S02.M1–M3 accepted as 07 work |
| 03-plan-tooling | no | — | skipped | no new Cursor rules expected |
| 04-tech-plan | no | — | skipped | Lean — tasks fit 01→07 |
| 05-verify-tech | no | — | skipped | — |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | **in_progress** | matrix/provenance + ticket close/children; S02.M1–M3 |
| 08-verify-build | yes | delta | pending | lint/type/tests on changed paths |
| 09-qa | no | — | skipped | Lean+07/08 — docs/matrix; 08 covers gates |
| 10-e2e | no | — | skipped | no UI |
| 11-verify-impl | yes | delta | pending | AC sign-off |
| 12-verify-deploy | no | — | skipped | waive expected (no runtime) |
| 13-deploy-smoke | no | — | skipped | waive expected with 12 |

## Skip rationale

Docs + coverage/provenance matrix dispositions for #869/#870/#872. No new deps, no formal
04 plan, no browser UJ, no deploy surface. Skip 09 — 08-verify-build + provenance tests
sufficient for Lean matrix work (same pattern as tooling-only lean variants).

## Approval

| Gate | Decision | Date |
|------|----------|------|
| Phase 0 | Q1=1, Q2=1, Q3=1, Q4=1 | 2026-08-05 |
| Proceed / routing | G2=1 proceed → 01 | 2026-08-05 |
| AC gate (01) | AC=1 approve AC1–AC4 → close 01 → start 02 | 2026-08-05 |
| Gate A / 02 | **PASS** (`D-S045-02-gate-a`) GateA=1 — S02.M1–M3 as 07 → start 07 | 2026-08-05 |
