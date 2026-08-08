# Routing plan — S052 / EV-043

**Preset:** Standard (**approved** via Evolve Plan Card)  
**Route:** `00 → 16 → 01 → 02 → 03 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
**Skip:** `06-tech-tooling`  
**Branch:** `evolve/EV-043-doks-staging-prod`  
**Features:** deepen **F30**  
**Issues:** [#886](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/886)  
**Status:** in_progress

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | S052 open |
| 16-evolve | yes | orchestrator | **in_progress** | Phase A→C |
| 01-requirements | yes | delta | **in_progress** | F30 deepen AC |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | yes | delta | pending | promote-from-stage rule |
| 04-tech-plan | yes | delta | pending | execution-plan |
| 05-verify-tech | yes | delta | pending | Gate B |
| 06-tech-tooling | no | — | skipped | no new deps |
| 07-build | yes | full | pending | overlays + CI + CLI |
| 08-verify-build | yes | delta | pending | |
| 09-qa | yes | delta | pending | staging smoke mapping |
| 10-e2e | yes | delta | pending | staging H4–H5 |
| 11-verify-impl | yes | delta | pending | |
| 12-verify-deploy | yes | delta | pending | dual env_role |
| 13-deploy-smoke | yes | delta | pending | staging then prod path |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 06 | No new language/runtime dependency inventory change |
