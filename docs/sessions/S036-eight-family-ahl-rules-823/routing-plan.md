# Routing plan — S036-eight-family-ahl-rules-823

**Preset:** Standard — **approved** `D-S036-open` Q5=1  
**Orchestrator:** 16-evolve · **Cycle:** EV-029  
**Path:** `00→16→01→02→04→07→08→09→10→11→12→13`  
**Skip:** `03, 05, 06` (re-add if 04 introduces new deps/ADR tooling/guardrails)  
**Skills in build:** `mine-domain-sources` (Phase A); product engines in Phase B

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Intake locked `D-S036-open` = 1,1,1,1,1,1 |
| 16-evolve | yes | orchestrator | **in_progress** | Phase 0–1 locked; orchestrating 01 |
| 01-requirements | yes | delta | **in_progress** | F28 + UJ-043 + TC-EV029/F28 written; Manifest+close pending |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | no | — | skipped | Re-add if new rules/hooks needed |
| 04-tech-plan | yes | delta | pending | Exec plan: Phase A mine → Phase B per family |
| 05-verify-tech | no | — | skipped | Re-add if new deps |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | pending | Mining + engine deltas + fixtures |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | yes | delta | pending | Standard preset |
| 10-e2e | yes | smoke | pending | Convert/lint/validate + catalog fixtures |
| 11-verify-impl | yes | delta | pending | Per–acceptance-criterion for each Fn |
| 12-verify-deploy | yes | delta | pending | Config/env if AHL surface ships |
| 13-deploy-smoke | yes | full | pending | When behavior ships to prod |

## Skip rationale

Standard on an existing app: specs → tech plan → build → full verify/deploy path. No new
deployable or greenfield tooling expected; skip 03/05/06 unless 04 surfaces inventory/ADR needs.
Routine Standard checkpoints after phases A–D and deploy.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open / Phase 0 | `D-S036-open` = **1,1,1,1,1,1** — S036+EV-029; mine-then-implement; AHL→…→SWXA order; shared AHL in-cycle; Standard; UI N/A | 2026-08-01 |
| Routing | Standard path above | 2026-08-01 |
| Exclude | SIGWX / VONA / QVACI; sink UI; #806 WIS2 mining | 2026-08-01 |
| Fn allocation | `D-S036-fn` = **1,1,1,1** — F28 + deepen; absorb #738/#820/#740; start 01; commit open @ `49e2a62` | 2026-08-01 |
)
