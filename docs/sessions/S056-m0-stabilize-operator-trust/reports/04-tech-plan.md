# 04-tech-plan — S056 / EV-047

**Status**: completed — `D-S056-04-plan=2` (laptop seed + CI re-record T1.3)  
**Date**: 2026-08-08  
**Mode**: delta

## Artifacts

| Path | Role |
|------|------|
| `reports/execution-plan.md` | Milestones M1–M4 / tasks T1–T4 |
| `build-plan-card.md` | 07 Plan handoff |
| Laptop spike | Local convert p95 (not authoritative) |

## Ruleset path (`D-S056-ruleset-defer=2`)

User chose: **defer requiring** `Converter perf (tac2iwxxm)` until the job ships in M1
T1.4; then apply at T1.5. Clears Gate A chicken/egg; keeps D-S056-gateA=2 intent.

## Baseline strategy

1. Implement recorder + gate harness (T1.1–T1.2)  
2. **Establish baseline** on CI-class runner → commit `tests/perf/baselines/converter_pr.yaml` (T1.3)  
3. Hard gate compares PR runs against that file (T1.4)  
4. Ruleset require check (T1.5)

Laptop spike (macOS) is informational only — see execution-plan table.

## Next

AskQuestion approve tech decisions + plan → 05 → 07 M1.
