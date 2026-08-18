# Verification Report

> Generated: 2026-08-18  
> Scope: Standard **08-verify-build** — EV-060 M1 AHL bulletin quality (#1001)  
> Branch: `evolve/EV-060-converter-operator-bugs`  
> Corpus: [Corpus: product §F6] [Corpus: tests §TC-EV060-1001] [Corpus: decisions §EV-060]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 1 test file | 1 ruff format | ruff format + prettier |
| Lint | PASS | 0 | 0 | ruff + eslint |
| Typecheck | PASS | warnings only (pre-existing auth/tac2iwxxm) | — | basedpyright + tsc |
| Tests (local `make test-unit`) | PASS | exit 0 after VAA AHL keep-whole fix | — | pytest matrix |
| H0c CORS | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| M1 AHL (TC-EV060-1001) | PASS | heading COM + `INVALID_AHL` + lint-tac parity | — | tac-validate + backend unit |
| Security (gitleaks) | PASS | none | — | `make secrets-check` |
| pip-audit | SKIPPED / advisory | not in default env | — | — |
| Performance | SKIPPED | N/A this milestone | — | — |
| Data | SKIPPED | N/A | — | — |
| Template layout | PASS | new files under `packages/tac-validate` + backend tests | — | static+api+worker |

**Overall: PASS**

## Fix-verify loop (1 of 3)

First `make test-unit` failed 2 tests:

- `packages/tac2iwxxm/tests/test_tc_ev029_005_vaa_gap_fixtures.py::test_vaa_product_order_lint_convert_validate`
- `packages/tac2iwxxm/tests/test_tc_ev029_007_product_order_smoke.py::test_product_order_lint_convert_validate[VAA]`

Cause: AHL lint required `=`-terminated slices. Annex 3 `vaa_a7_2.tac` is `FV…` AHL + `VA ADVISORY` body with no `=`, so lint emitted bulletin `INVALID_AHL` (“contains no TAC reports”). User chose **fix implementation** (`D-S070-08-vaa`). Remainder without `=` is now one contained report (same keep-whole rule as `tac2iwxxm.bulletin` for VAA/TCA/SWXA/VONA). Heading-only AHL still yields `INVALID_AHL`.

Re-run: those two tests + `make test-unit` **PASS**. Per-file coverage on `ahl.py` restored ≥95% with heading-without-newline + `_ahl_heading_ok` cases.

## Connectivity

- Blocking H0c `tests/unit/test_cors_policy.py`: **PASS**
- Artifacts present: `tests/smoke/test_staging_connectivity.py`, `scripts/deploy/verify_connectivity.sh`
- CORS: `CORSMiddleware` in `apps/backend/src/api.py` via `get_cors_origins()`
- H4–H5 / staging: **deferred** to 12/13 (`D-S070-cors`); M1 ships through existing `/lint-tac`

## Next

PR M1 → `stage` (#1001 In review). Then 07-build M2 (#1003 IWXXM product pass-through). Promote held.
