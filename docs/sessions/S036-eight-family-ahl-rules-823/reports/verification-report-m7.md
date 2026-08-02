# 08-verify-build — M7 boundary (EV-029 / S036)

**Date**: 2026-08-02  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Scope**: Milestone M7 — TC SIGMET (F23 deepen / #738)

## Checks

| Check | Result |
|-------|--------|
| `make test-tc-sigmet-quality` | **PASS** (gap fixtures 13; convert-bulletin TC; keyword pack 14 incl. WC→LY AHL) |
| T7.1 fixtures | **PASS** (13/13 `test_tc_ev029_007_tc_sigmet_gap_fixtures`) |
| T7.2 WC split + TC CNL root | **PASS** (`TropicalCycloneSIGMET` root/CNL; convert-bulletin CCA) |
| Pre-commit on T7.3 | **PASS** (hooks on commit) |

## Deliverables

| Task | Summary |
|------|---------|
| T7.1 | TC SIGMET gap fixtures: WC BBB matrix + CNL AHL + multi-report + TCA non-confusion |
| T7.2 | WC `split_bulletin`; `TropicalCycloneSIGMET` emit/CNL; 6h WC lint; convert-bulletin CCA |
| T7.3 | `tc-sigmet-quality.yml` + `make test-tc-sigmet-quality` (E29-T4 separate family pack) |

## Connectivity

No FE change; H4–H5 remain waived (E29-T6).

## Next

**T7.4** — close or child-issue #738 residuals; then M8 AIRMET @ T8.1.
