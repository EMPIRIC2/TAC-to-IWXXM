# Verification Report — S071 / EV-061 M2 (#1012)

> Generated: 2026-08-19  
> Scope: 07-build M2 AHL decode + convert-bulletin  
> Branch: `evolve/EV-061-pre-promote-ux-catalog`  
> Corpus: [Corpus: product §F6] [Corpus: product §F9] [Corpus: api] [Corpus: tests §TC-EV061-1012]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | decode.py + convert-bulletin mapping | Ruff format on api.py / decode.py | `ruff check` |
| Format | PASS | Two files reformatted during implement | yes | `ruff format` |
| Typecheck (delta) | PASS | `decode.py` and `api.py` 0 errors | no | `basedpyright` |
| Tests (delta) | PASS | TC-EV061-1012-001..004 + F6-030 + decode regression (65) | no | pytest |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` 6 passed | no | pytest |
| H0i | PASS | 10 passed in `test_h0i_connectivity.py` (backend package). Isolated run trips coverage fail-under; tests themselves passed | no | pytest |
| Security | N/A | No new deps | — | — |
| Template | N/A | No new deployable | — | — |

## M2 acceptance

- Golden `SAUS31 KZNY` multi-METAR AHL decodes with heading row + per-report F9 segments (KJFK and KLGA). Heading is not a residual; second METAR is not dumped as `METAR KLGA`.
- Convert-bulletin golden still HTTP 200 with two IWXXM results (already true; locked by TC-EV061-1012-002).
- Malformed heading → HTTP 422 `INVALID_AHL` with `detail.alias=bulletin_split_failed` (`D-S071-ahl-code`). Heading-only → `empty_bulletin`. Operator messages have no internal doc refs.
- FileConverter AHL path still calls convert-bulletin with product/profile; toast shows operator error copy.

## Next

08-verify-build M2 PASS. Push M2 commits onto [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016) (same evolve branch → `stage`) or stacked M2 PR. Then 07-build **M3 #1010** (Validate IWXXM readable decode). Promote held until #1015.
