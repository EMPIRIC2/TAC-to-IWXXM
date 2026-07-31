# 04-tech-plan report — S032 / EV-025

**Date**: 2026-07-31  
**Mode**: delta  
**Status**: **draft plan ready** — Gate B pending

## Batch T locks (user: `1,1,2,1,3,1`)

| ID | Vote | Lock |
|----|------|------|
| E25-T1 | 1 | M0→#810→#811→#812→adjacent→#809→validate→Gate C audit/smoke |
| E25-T2 | 1 | Per dig type/row encode (+lint) goldens |
| E25-T3 | 2 | AskQuestion per new dep |
| E25-T4 | 1 | Lane A then Lane B |
| E25-T5 | 3 | Dig ❌ encode residual **blocks Gate C** |
| E25-T6 | 1 | Draft plan from T1–T5 |

## Contradiction resolution

**S02.M2** (02-verify-plan) allowed residual dig types → child issues without blocking Gate C.  
**E25-T5=3** (04-tech-plan) is stricter and **supersedes** that soft deferral for **encode** residuals.

Unchanged: **S02.L1** — TC-EV025-010 may document Schematron deferrals without blocking Lane A encode goldens (SCH ≠ dig ❌ encode gap).

## Artifacts

- `reports/execution-plan.md` — 8 milestones / 28 tasks (draft)
- No new ADR (reuse ADR-028 registry, ADR-032 catalog equality)
- No dependency-inventory delta (prefer none; AskQuestion if needed)
- No deploy-plan delta (13 when ships; existing Render topology)

## Next

Gate B AskQuestion — approve milestones → Lean **07-build** @ T0.1 (05 skipped).

## Close

**Gate B=1** (2026-07-31) — plan approved; handoff **07-build** @ T0.1 (`D-S032-04-plan-approve`).
