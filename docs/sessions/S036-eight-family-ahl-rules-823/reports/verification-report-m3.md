# 08-verify-build — M3 boundary (EV-029 / S036)

**Date**: 2026-08-02  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Scope**: Milestone M3 — SPECI (F20 deepen)

## Checks

| Check | Result |
|-------|--------|
| `make test-speci-quality` | **PASS** (gap fixtures 11; convert-bulletin SPECI; SPECI keyword packs) |
| T3.1 fixtures | **PASS** (11/11 `test_tc_ev029_007_speci_gap_fixtures`) |
| T3.2 convert-bulletin SPECI CCA | **PASS** (`test_convert_bulletin_speci_ahl_bbb_report_status`) |
| Pre-commit on T3.1–T3.2 + semver bump | **PASS** |

## Deliverables

| Task | Summary |
|------|---------|
| T3.1 | SPECI gap fixtures: AHL BBB matrix + multi-report + product-order `speci_a3_2` |
| T3.2 | HTTP convert-bulletin SPECI CCA → `report_status` (shared M2 encode surface) |
| T3.3 | `speci-quality.yml` + `make test-speci-quality` |

## Semver

`tac2iwxxm` **0.1.1 → 0.2.0** (`D-S036-semver-minor`); no tags / PyPI publish.

## Connectivity

No FE change; H4–H5 remain waived (E29-T6).

## Next

Open minor PR for M3 (or extend #828 with M3 tip); continue **M4 @ T4.1** (TAF deepen).
