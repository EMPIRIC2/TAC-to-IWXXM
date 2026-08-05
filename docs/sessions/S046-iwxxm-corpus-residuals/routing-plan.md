# Routing plan — S046 / EV-038

**Preset:** Standard (+05 for B→C)  
**Route:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
**Skip:** `03-plan-tooling`, `06-tech-tooling`  
**Branch:** `evolve/EV-038-iwxxm-corpus-residuals`  
**Features:** deepen **F2 / F4 / F6 / F7 / F32** (no new Fn expected)  
**Status:** in_progress — D-S046-mplan locked; **01-requirements**  
**Milestones:** M1 docs (#858/#861/#855) → M2 release-line (#851–#854) → M3 soft (#859/#860/#857) → M4 encode (#849/#850/#856)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | S046 open; D-S046-mplan Q1=1 Q2=1 Q3=1 |
| 16-evolve | yes | orchestrator | **in_progress** | Phase 0/1 locked |
| 01-requirements | yes | delta | **completed** | **D-S046-ac** AC=1 approve AC1–AC14 |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS (`D-S046-02-gate-a`=2 + `D-S046-sot`=1) |
| 03-plan-tooling | no | — | skipped | no new Cursor rules expected |
| 04-tech-plan | yes | delta | **in_progress** | execution-plan milestones |
| 05-verify-tech | yes | delta | pending | B→C with 04 |
| 06-tech-tooling | no | — | skipped | no new dep tooling expected |
| 07-build | yes | full | pending | per milestone |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | yes | delta | pending | Standard |
| 10-e2e | yes | delta | pending | #854 UI / picker |
| 11-verify-impl | yes | delta | pending | — |
| 12-verify-deploy | yes | delta | pending | runtime when M2+/encode ships |
| 13-deploy-smoke | yes | delta | pending | with 12 |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new Cursor rules / hooks planned |
| 06 | No new dependency inventory tooling expected; back-add deps in 04 if needed |

## Gates

| Gate | Result | When |
|------|--------|------|
| Phase 0 open | **PASS** (`D-S046-open`) | 2026-08-05 |
| Milestone plan | **PASS** (`D-S046-mplan`) M1→M2→M3→M4; UI yes@M2 | 2026-08-05 |
| A→B / 02 | **PASS** (`D-S046-02-gate-a`=2 + `D-S046-sot`=1) | 2026-08-05 |
| B→C / 05 | pending | — |
| C→D / 11 | pending | — |
| Deploy 12/13 | pending | may waive per-milestone if docs-only |
