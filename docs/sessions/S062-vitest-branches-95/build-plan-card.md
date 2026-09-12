# Build Plan Card — S062 / EV-053

> Updated: 2026-08-10 · Cycle EV-053 · Session S062-vitest-branches-95

## Goal

Close [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968): Vitest `branches` ≥95
with `FileConverter.tsx` re-included; FileConverter file branches ≥95; resolve
`D-S061-cov-branches` waiver.

## Out of scope

Lowering other thresholds; #874/#727/#836; stage→main; UI redesign; new deps.

## Locked

- Standard routing; Gate A PASS (`D-S062-gateA=1`); M1 AC5 verify-report proof
- Re-include FileConverter; AC1–AC5 / TC-EV053-001..005
- 05 skipped

## Proposed tech (await `D-S062-04-plan`)

| ID | Choice |
|----|--------|
| AC5 proof | Coverage JSON + session verify reports |
| Config | Remove FileConverter exclude; `branches: 95` |
| Tests | Extend `FileConverter.test.tsx` |
| Inventory | Resolve waiver in S061 inventory YAML |

## Milestones

1. **M1** — Config + baseline (T1.1–T1.3)
2. **M2** — FileConverter branch fill (T2.1–T2.3)
3. **M3** — Inventory/docs/CI closeout (T3.1–T3.3)

## Next after approval

Skip 05 → **07-build M1** (T1.1).

## Risks

- FileConverter ~2.6k LOC — M2 may need multiple commits/iterations
- Must not drop lines/stmts/funcs below 95 while raising branches
