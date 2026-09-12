# T4.4 — TC-F20-001 registry completeness (M4 close)

**Session**: S020-aerodrome-quality · **Cycle**: EV-015 · **Date**: 2026-07-22

## Result

**PASS** — M4 closed. TC-F20-001 green via
`packages/tac-validate/tests/test_tc_f20_001_registry_completeness.py` (7 tests).

## Coverage

| Check | Result |
|-------|--------|
| TAF/SPECI fixture emissions ⊆ registry | PASS |
| TAF/SPECI `expected_codes` ⊆ registry (all manifest sections) | PASS |
| Every `product=taf` registry row has fixture `expected_codes` | PASS |
| ISSUE_CATALOG includes taf/speci-tagged rows | PASS |
| `catalog_entries(product=taf\|SPECI)` filters | PASS |
| Static scan `rules.py` / `product_rules.py` codes registered | PASS |
| Unknown-code KeyError gate | PASS |

## Package suite

`uv run pytest packages/tac-validate/tests/` → **471 passed**

## Next

M5 T5.1 — Vitest catalog panel filters/copy for TAF tags (E15-14; TC-F20-005).
