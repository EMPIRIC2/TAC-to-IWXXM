# 08-verify-build — M10 boundary (EV-029 / S036)

**Date**: 2026-08-02  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Scope**: Milestone M10 — TCA (F27 deepen / #820)

## Checks

| Check | Result |
|-------|--------|
| `make test-tca-quality` | **PASS** (gap fixtures 16; convert-bulletin TCA; F27 lint + convert keep-green) |
| T10.1 fixtures | **PASS** (16/16 `test_tc_ev029_005_tca_gap_fixtures`) |
| T10.2 FK split + reportStatus | **PASS** (`split_bulletin` FK; BBB→`reportStatus`) |
| Pre-commit on T10.3 | **PASS** (hooks on commit) |

## Deliverables

| Task | Summary |
|------|---------|
| T10.1 | TCA gap fixtures: FK BBB matrix + `=` multi-report + blank-line guard + A2-2 product-order + RMK/NO MSG nilReasons + decode allowlist |
| T10.2 | FK `split_bulletin`; `reportStatus` emit; convert-bulletin CCA |
| T10.3 | `tca-quality.yml` + `make test-tca-quality` (E29-T4 separate family pack) |

## Connectivity

No FE change; H4–H5 remain waived (E29-T6).

## Next

**M11 @ T11.1** — SWXA registry + accept/negative fixtures (F28).
