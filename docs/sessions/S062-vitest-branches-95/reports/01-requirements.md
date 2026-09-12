# 01-requirements — S062 / EV-053

**Status**: completed — `D-S062-01-ac=1`  
**Date**: 2026-08-10  
**Mode**: delta (deepen F29, M5 — Vitest branches / FileConverter)  
**Issues**: [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968)
(parent [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950) / EV-052)

## Corpus

[Corpus: product §F29] [Corpus: product §M5] [Corpus: tests] [Corpus: adr/ADR-007]
[Corpus: decisions §EV-052] [Corpus: decisions §EV-053]

## Standing doc deltas

| Doc | Change |
|-----|--------|
| `docs/feature-list.md` | F29/M5 deepen block EV-053 / #968 |
| `docs/test-plan.md` | TC-EV053-001..005 |
| `docs/decisions/evolve-decisions.md` | AC1–AC5 locked; strategy decisions |
| `docs/decisions/requirements-decisions.md` | EV-053 section |
| Coverage inventory | Resolve `branch_waiver` in **07** (AC3) |

## Skipped (N/A this cycle)

- Spec / user-journeys / API / deploy / env (no product surface)
- New Fn id
- UI preview (`D-S062-ui-preview=2`)
- H4–H5 connectivity (CI-only)
- ADR-007 rewrite (Q2=1 — cite existing; no amend required)

## Locked decisions (`D-S062-01-ac=1`)

| ID | Choice |
|----|--------|
| D-S062-fc-strategy | **1** — Re-include FileConverter; fill tests to ≥95 |
| D-S062-01-manifest | **1** — Delta manifest as drafted |
| D-S062-01-ac | **1** + Q3=**2** — AC1–AC4 + **AC5** FileConverter ≥95% branches |

## Acceptance criteria

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Vitest `branches` ≥95 (lines/stmts/funcs remain ≥95) | TC-EV053-001 |
| AC2 | FE coverage suite green with FileConverter included | TC-EV053-002 |
| AC3 | Inventory `branch_waiver` resolved | TC-EV053-003 |
| AC4 | Docs cite closeout; #968 closable | TC-EV053-004 |
| AC5 | FileConverter file branch coverage ≥95% when included | TC-EV053-005 |

## Next

**02-verify-plan** (Gate A).
