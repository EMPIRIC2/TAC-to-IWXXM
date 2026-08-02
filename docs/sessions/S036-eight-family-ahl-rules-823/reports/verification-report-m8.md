# 08-verify-build — M8 boundary (EV-029 / S036)

**Date**: 2026-08-02  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Scope**: Milestone M8 — AIRMET (F24 deepen)

## Checks

| Check | Result |
|-------|--------|
| `make test-airmet-quality` | **PASS** (gap fixtures 12; convert-bulletin AIRMET; F24 lint + convert keep-green) |
| T8.1 fixtures | **PASS** (12/12 `test_tc_ev029_007_airmet_gap_fixtures`) |
| T8.2 WA split + AIRMET CNL | **PASS** (`split_bulletin` WA; BBB→`reportStatus`; CNL cancel) |
| Pre-commit on T8.3 | **PASS** (hooks on commit) |

## Deliverables

| Task | Summary |
|------|---------|
| T8.1 | AIRMET gap fixtures: WA BBB matrix + CNL AHL + multi-report + A6-1a-TS product-order |
| T8.2 | WA `split_bulletin`; `reportStatus` emit; CNL AIRMET parse/emit; convert-bulletin CCA |
| T8.3 | `airmet-quality.yml` + `make test-airmet-quality` (E29-T4 separate family pack) |

## Connectivity

No FE change; H4–H5 remain waived (E29-T6).

## Next

**M9 @ T9.1** — VAA bulletin/encode residual fixtures (#820).
