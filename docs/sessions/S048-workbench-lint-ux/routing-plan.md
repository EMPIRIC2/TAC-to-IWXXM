# Routing plan — S048 / EV-040

**Preset:** Standard (+05 for B→C)  
**Route:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
**Skip:** `03-plan-tooling`, `06-tech-tooling`  
**Branch:** `evolve/EV-040-workbench-lint-ux`  
**Features:** deepen **F7 / F10 / F15** (no new Fn)  
**Status:** in_progress — 13 smoke baseline green; merge pending for tip CD  
**Approved:** 2026-08-06 (plan + intake)  
**PR:** https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/893

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | S048 open |
| 16-evolve | yes | orchestrator | **in_progress** | EV-040 close after merge |
| 01-requirements | yes | delta | **completed** | AC1–AC7 |
| 02-verify-plan | yes | delta | **completed** | Gate A |
| 03-plan-tooling | no | — | skipped | No new Cursor rules |
| 04-tech-plan | yes | delta | **completed** | Execution plan |
| 05-verify-tech | yes | delta | **completed** | Gate B |
| 06-tech-tooling | no | — | skipped | No new publish deps |
| 07-build | yes | full | **completed** | M1 UX + M2 catalog/lint |
| 08-verify-build | yes | delta | **completed** | |
| 09-qa | yes | delta | **completed** | qa-report.md |
| 10-e2e | yes | full | **completed** | H4–H5 live; UI local preview |
| 11-verify-impl | yes | delta | **completed** | verify-impl.md |
| 12-verify-deploy | yes | delta | **completed** | deploy-checklist approved |
| 13-deploy-smoke | yes | delta | **completed*** | H1–H5 PASS + CI green; *tip CD after merge approval |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new plan-adherence rules |
| 06 | Catalog join uses existing domain JSON/MD; no new publish deps |
