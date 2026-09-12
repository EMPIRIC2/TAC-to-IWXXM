# 01-requirements summary — S043 / EV-035

**Stage:** 01-requirements (delta)  
**Date:** 2026-08-05  
**Mode:** evolve · deepen-only (no new Fn)

## Locked gates

| Gate | Choice | Meaning |
|------|--------|---------|
| G1 | 2 | Deepen **F6 / F12 / F15 / F2** only — standing provenance under `docs/domain/rules/`; **no F33** |
| G2 | 1 | Standard routing approved |
| G3 | 1 | Path-cite `[docs/domain/…]` — no CORPUS membership this cycle |
| G4 | 1 | Proceed 01 → 02 |

Phase 0: Q1=3, Q2=4, Q3=1, Q4=2 (+ dense asserts). UI: **N/A**.

## Spec deltas written

| Doc | Change |
|-----|--------|
| [feature-list.md](../../feature-list.md) | Summary + F2/F6/F12/F15 deepen EV-035 ACs |
| [test-plan.md](../../test-plan.md) | **TC-EV035-001..006** dense provenance asserts |
| [evolve-decisions.md](../../decisions/evolve-decisions.md) | G1–G4 + corpus path-cites |
| Session brief / routing | Remove F33; deepen-only |

## Acceptance (shared)

1. Provenance map: digs reviewed ↔ rules extracted ↔ sources  
2. Full stack: ISSUE_CATALOG + encode/SCH + bulletin AHL  
3. Dense CI asserts per cited/revisited rule (TC-EV035-*)  
4. Gaps raised to user — no silent invent  
5. Reuse F29 harness patterns where useful (no F29 Fn deepen required)

## Corpus cites

- `[Corpus: product]` — feature-list deepen  
- `[Corpus: tests]` — test-plan TC-EV035  
- `[docs/domain/README.md]` · `RULE_SOURCE_URLS` · `COVERAGE_MATRIX` · `ISSUE_CATALOG`  
- `[Corpus: WAIVED — domain CORPUS membership; reason: G3=1 path-cite; decided: EV-035]`

## Early gaps (raise — confirm disposition in 02/07)

| Gap | Notes |
|-----|-------|
| VONA encode Guidance-silent | Cookbook + XSD/SCH only |
| US REMARKS encode cells ⚠ | Many COVERAGE_MATRIX iwxxm_us rows partial |
| ISSUE_CATALOG thin cites | Theme tags without RULE_SOURCE_URLS linkage |
| Bulletin non-METAR AHL | Family gaps in matrix |

## Next

**02-verify-plan** (Gate A) — consistency pass + gap disposition interview.
