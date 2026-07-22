# T5.3 — API smoke `product=taf` + `product=speci` (TC-F20-005)

**Session**: S020-aerodrome-quality · **Cycle**: EV-015 · **Date**: 2026-07-22

## Result

**GREEN** — in-process authenticated smoke for lint+convert + catalog GET (H3-shaped; live H3/H4–H5 reuse same paths at T5.7).

| Check | Detail |
|-------|--------|
| Lint | `POST /api/v1/lint-tac` TAF + SPECI accept fixtures → `ok`; codes ⊆ registry |
| Convert | `POST /api/v1/convert` annex3 → XML contains `iwxxm` + product root hint |
| Catalog | `GET /api/v1/lint-issue-catalog?product=taf\|speci` → non-empty; TAF has `MISSING_VALIDITY`; SPECI has `MISSING_CCCC` |

## Module

`apps/backend/tests/integration/test_tc_f20_005_taf_speci_catalog_smoke.py`

## Verification

```text
cd apps/backend && uv run pytest \
  tests/integration/test_tc_f20_005_taf_speci_catalog_smoke.py -v --no-cov
# 4 passed
```

## Next

T5.4 — 08-verify-build (lint/typecheck/format/full suites). Evolve PR still waits until M5 / Phase D.
