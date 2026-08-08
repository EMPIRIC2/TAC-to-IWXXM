# Routing plan — S056 / EV-047

**Preset:** Standard (**approved** `D-S056-preset=1`)  
**Route:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`  
**Skip:** `03`, `06`, `10`, `12`, `13`  
**Branch:** `evolve/EV-047-m0-stabilize-operator-trust` (base `stage`)  
**Features:** deepen **M5**, **F6**, **F7** (no new Fn)  
**Issues:** [#833](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/833),
[#834](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/834),
[#956](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/956),
[#957](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/957)  
**Status:** in_progress — Phase 0–1

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | S056 open (`D-S056-open=1`) |
| 16-evolve | yes | orchestrator | **in_progress** | Phase 0–1; remaining intake #834/#956/#957 |
| 01-requirements | yes | delta | pending | |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | no | — | skipped | unless new Cursor rules |
| 04-tech-plan | yes | delta | pending | husky + perf harness + docs tasks |
| 05-verify-tech | yes | delta | pending | Gate B |
| 06-tech-tooling | no | — | skipped | no new runtime deps expected |
| 07-build | yes | full | pending | |
| 08-verify-build | yes | delta | pending | |
| 09-qa | yes | delta | pending | |
| 10-e2e | no | — | skipped | re-enable if help-link UI |
| 11-verify-impl | yes | delta | pending | |
| 12-verify-deploy | no | — | skipped | waived unless help-link deploy |
| 13-deploy-smoke | no | — | skipped | waived unless help-link deploy |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new Cursor rules/hooks expected beyond husky/pre-commit edits |
| 06 | No new runtime dependency inventory change expected |
| 10 | No browser UI unless help entry ships; re-route if needed |
| 12 / 13 | CI/docs cycle; merge gate is tip CI green → `stage` (D-S056-preset=1) |
