# M1 baseline — FE coverage after FileConverter re-include

**Date:** 2026-08-10  
**Tip context:** EV-053 T1.1 config (FileConverter in set; `branches: 95`)  
**Command:** `pnpm --filter @metar/frontend exec vitest run --coverage`  
**Result:** **RED** (expected) — aggregate thresholds not met; FileConverter under AC5

## Aggregate (Vitest summary)

| Metric | Pct | Threshold |
|--------|-----|-----------|
| Statements | 94.29% | 95 |
| Branches | 84.5% | 95 |
| Functions | 95.97% | 95 (pass) |
| Lines | 94.9% | 95 |

## FileConverter.tsx (from `coverage-final.json`)

| Metric | Hit/Total | Pct | AC5 target |
|--------|-----------|-----|------------|
| Statements | 596/706 | 84.42% | — |
| Branches | 394/543 | 72.56% | **≥95** |
| Functions | 121/138 | 87.68% | — |
| Uncovered branch arms | 149 | — | close in M2 |
| Uncovered stmt lines | 108 | — | fill as needed for aggregate |

## Notes

- Re-including FileConverter dropped aggregate lines/stmts slightly below 95 and left
  branches ~84.5% (same ballpark as pre-EV-052 waiver).
- M2 must raise **FileConverter branches** to ≥95 (AC5) and restore aggregate
  lines/stmts/branches ≥95 (AC2). Functions already clear.

## Corpus

[Corpus: tests] [Corpus: adr/ADR-007] [Corpus: decisions §EV-053]
