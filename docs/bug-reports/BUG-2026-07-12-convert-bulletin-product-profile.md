# BUG-2026-07-12-convert-bulletin-product-profile

| Field | Value |
|-------|-------|
| **Status** | resolved |
| **Feature** | F6 (convert-bulletin / tac2iwxxm cutover) |
| **Severity** | high |
| **Classification** | code bug |
| **Remediation path** | PR #706 / PRM-012 |
| **GitHub** | [PR #706 review](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/706) |

## Error description

`POST /api/v1/convert-bulletin` accepts required `product` and optional `profile` form fields but does not pass them to `convert_metar_tac_with_metadata` after the gifts→tac2iwxxm cutover. Non-METAR bulletin reports are converted as METAR (auto-detect) and fail or mis-emit; `iwxxm_us` profile is ignored (`_ = profile` stub).

## Error logs

Bugbot (18-pr-review PRR-009):

```
convert-bulletin ignores profile parameter — apps/backend/src/api.py:799-860
Non-METAR products default to METAR — convert_metar_tac_with_metadata via _detect_product
```

## Investigation

1. Confirmed on `feat/S008-M4-us-metar`: convert call at ~856–860 omits `product=` / `profile=`.
2. Pre-cutover gifts path was METAR-centric; cutover makes the missing kwargs a functional F6.bulletin regression.
3. Repro test: `apps/backend/tests/unit/test_bug_2026_07_12_convert_bulletin_product_profile.py` (backend unit path so `src` imports resolve)

## Repro test

| Path | Status |
|------|--------|
| `apps/backend/tests/unit/test_bug_2026_07_12_convert_bulletin_product_profile.py` | green |

## Fix

Pass `product=product` and `profile=profile` into `convert_metar_tac_with_metadata`; remove `_ = profile` stub.
