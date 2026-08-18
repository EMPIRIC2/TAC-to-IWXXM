# 07-build M1 — AHL bulletin quality (#1001)

**Status:** implementation complete; 08-verify-build **PASS** (2026-08-18)  
**Corpus:** [Corpus: product §F6] [Corpus: product §F7] [Corpus: tests §TC-EV060-1001]

## Tasks

| ID | Result |
|----|--------|
| T1.1 | Red tests in `test_tc_ev060_1001_ahl_heading.py` + lint-tac unit |
| T1.2 | `tac_validate.lint` splits WMO AHL; heading COM (`INVALID_AHL`); reports lint as product |
| T1.3 | `/lint-tac` uses the same lint; parity test vs `/convert-bulletin`. Workbench/FileConverter call `/lint-tac`. |
| T1.4 | Reuse `metar_multi_ahl.txt` / A3-1 AHL fixture; no new fixture file |

## Notes

- No new npm/PyPI deps. Registry code `INVALID_AHL` (operator copy has no planning ids).
- convert-bulletin empty/malformed HTTP codes unchanged (400/422); lint-tac returns 200 + structured `INVALID_AHL`.
- 08 loop: VAA AHL without `=` was empty-bulletin `INVALID_AHL`; remainder keep-whole when no `=` split (`D-S070-08-vaa`).
