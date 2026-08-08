# Routing plan — S054 / EV-045

**Preset:** Standard (**approved** `D-S054-open=1`)  
**Route:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`  
**Skip:** `03`, `06`, `10`, `12`, `13`  
**Branch:** `evolve/EV-045-rust-ci`  
**Features:** deepen **F13**, **F14**  
**Issues:** [#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725)  
**Status:** in_progress

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | S054 open |
| 16-evolve | yes | orchestrator | **in_progress** | Phase B — 05-verify-tech |
| 01-requirements | yes | delta | **completed** | D-S054-01-ac=1 |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS; D-S054-ac6-waive=2 |
| 03-plan-tooling | no | — | skipped | no new Cursor rules/hooks |
| 04-tech-plan | yes | delta | **completed** | D-S054-04-plan=1 |
| 05-verify-tech | yes | delta | **completed** | D-S054-gateB=1 |
| 06-tech-tooling | no | — | skipped | toolchain already ADR-017 |
| 07-build | yes | full | **in_progress** | T1.1… |
| 08-verify-build | yes | delta | pending | |
| 09-qa | yes | delta | pending | map AC → CI job IDs |
| 10-e2e | no | — | skipped | no browser UI |
| 11-verify-impl | yes | delta | pending | AC checklist |
| 12-verify-deploy | no | — | skipped | CI-only; tip CI green |
| 13-deploy-smoke | no | — | skipped | no staging/prod deploy |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new Cursor rules/hooks expected |
| 06 | No new runtime dependency inventory change (maturin/rust already ADR-017) |
| 10 | No browser UI / Playwright journeys |
| 12 / 13 | CI-only change; merge gate is tip CI green, not deploy smoke |
