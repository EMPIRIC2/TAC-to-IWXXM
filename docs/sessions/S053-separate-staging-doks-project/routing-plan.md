# Routing plan — S053 / EV-044

**Preset:** Standard (**approved** 2026-08-08 `1:1`)  
**Route:** `00 → 16 → 01 → 02 → 03 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
**Skip:** `06-tech-tooling`  
**Branch:** `evolve/EV-044-separate-staging-doks` (from `main@d0a51f5a`)  
**Features:** deepen **F30**  
**Status:** in_progress

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | S053 open; decisions locked |
| 16-evolve | yes | orchestrator | **in_progress** | Phase A specs → Gate A |
| 01-requirements | yes | delta | **completed** | ADR-034 amend + F30 AC13 + deploy/test deltas |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | yes | delta | pending | dual-cluster kubeconfig / project rules |
| 04-tech-plan | yes | delta | pending | execution-plan + provision tasks |
| 05-verify-tech | yes | delta | pending | Gate B |
| 06-tech-tooling | no | — | skipped | no new runtime deps |
| 07-build | yes | full | pending | provision + CD + overlays/docs |
| 08-verify-build | yes | delta | pending | |
| 09-qa | yes | delta | pending | |
| 10-e2e | yes | delta | pending | staging H4–H5 on new LB |
| 11-verify-impl | yes | delta | pending | |
| 12-verify-deploy | yes | delta | pending | dual env_role + dual clusters |
| 13-deploy-smoke | yes | delta | pending | staging then prod path |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 06 | No new language/runtime dependency inventory change |
