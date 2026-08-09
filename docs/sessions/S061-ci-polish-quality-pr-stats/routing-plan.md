# Routing plan — S061 / EV-052

**Status:** approved (`D-S061-route=1`)  
**Preset:** **Standard** (`D-S061-intake` Q5=1)

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Opened S061 |
| 16-evolve | yes | orchestrate | **in_progress** | Agent (Plan switch declined) |
| 01-requirements | yes | delta | **completed** | `D-S061-01-ac=1`; `D-S061-redis=1` |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS (`D-S061-gateA=1`) |
| 03-plan-tooling | no | — | skipped | No new Cursor rule required unless Redis/Sentry convention lands |
| 04-tech-plan | yes | delta | **completed** | `D-S061-04-plan=1` |
| 05-verify-tech | yes | delta | **completed** | `D-S061-gateB=1` |
| 06-tech-tooling | no | — | skipped | Deps via 04 + inventory back-add |
| 07-build | yes | delta | **in_progress** | M1 T1.1–T1.5 |
| 08-verify-build | yes | delta | pending | |
| 09-qa | yes | delta | pending | |
| 10-e2e | no | — | skipped | No operator journey delta; unit/CI gates cover |
| 11-verify-impl | yes | delta | pending | |
| 12-verify-deploy | no | — | skipped | Waive unless Redis/Sentry needs live DOKS proof |
| 13-deploy-smoke | no | — | skipped | Waive; staging apply secrets later promote |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`

## Skip rationale

- Standard without 03/06/10/12/13: CI + library/SDK wiring; no new greenfield tooling skill; no UJ change; deploy secrets applied at promote / ops follow-up unless user upgrades.
- Re-enable 12/13 if Redis path requires live multi-replica proof on staging DOKS.
