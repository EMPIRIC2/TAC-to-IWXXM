# Routing plan — S060 / EV-051

**Status:** approved (`D-S060-route=1`)  
**Preset:** **Lean+**

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Opened S060 |
| 16-evolve | yes | orchestrate | **in_progress** | |
| 01-requirements | yes | delta | **completed** | AC1–AC6 locked |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS (await confirm) |
| 03-plan-tooling | yes | delta | **completed** | Rules updated |
| 04-tech-plan | no | — | skipped | |
| 05-verify-tech | no | — | skipped | |
| 06-tech-tooling | no | — | skipped | |
| 07-build | yes | delta | **completed** | `ci-cd.yml` amended |
| 08-verify-build | yes | delta | **completed** | verification-report.md |
| 09-qa | yes | delta | **completed** | qa-report.md |
| 10-e2e | no | — | skipped | |
| 11-verify-impl | yes | delta | **completed** | `D-S060-11-next=1` |
| 12-verify-deploy | no | — | skipped | |
| 13-deploy-smoke | no | — | skipped | |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 03 → 07 → 08 → 09 → 11`

Skip: `04`, `05`, `06`, `10`, `12`, `13` (unless user upgrades to Standard with 04/05).

## Skip rationale

- Config/CD/docs change deepening F30; no new Fn UI.
- 03 included because Cursor rule + promote semantics change.
- 04/05 optional: execution plan can live in session report if Lean stays.
- 12/13 waived: cycle ships workflow to `stage`; first tag-driven prod cutover is a later promote.
