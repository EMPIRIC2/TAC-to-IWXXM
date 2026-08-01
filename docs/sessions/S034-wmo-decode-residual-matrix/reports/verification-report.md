# 08-verify-build — S034 / EV-027

**Date**: 2026-07-31  
**Tip**: `994c3b1`  
**Issue**: #815

## Checks

| Check | Result |
|-------|--------|
| `make validate-fast` | PASS (pre-commit / format / typecheck / lint) |
| TC-EV027-001..002 inventory | PASS (4 tests) |
| TC-EV027-003 residual matrix | PASS (12 parametrized + allowlist guard) |
| TC-F9 SIGMET A6 residuals | PASS (regression) |
| examplesCatalog Vitest | PASS (20 tests) |

## Matrix outcome

| Peer class | Residuals |
|------------|-----------|
| METAR/SPECI/TAF/AIRMET + SIGMET TS/CNL | `[]` after decode fixes |
| VA SIGMET (EGGX + multi-location) | `[]` after geometry/eruption tokens |
| VAA / TCA | allowlisted (`allow_any`) — F9 G4 / ADR-025 · child [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) |

## Verdict

**PASS** — ready for 10-e2e smoke + PR / Gate C.
