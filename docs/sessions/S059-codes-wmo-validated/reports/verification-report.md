# 08-verify-build — S059 / EV-050

**Date:** 2026-08-09  
**Tip:** `48b6328d` (M1–M4 + membership prettier/coverage fix)  
**Corpus:** [Corpus: tests] [Corpus: tech-spec] [Corpus: product §F12]

## Scope

Delta after Phase C / M4 closeout + fix-in-place for CI membership/coverage gates.

## Checks

| Check | Result | Notes |
|-------|--------|-------|
| `make format-check` | PASS | ruff + prettier |
| `make lint-tac-validate` | PASS | ruff |
| `make typecheck-py` (tac-validate + siblings) | PASS | 0 errors (pre-existing tac2iwxxm warnings) |
| `make membership-check` | PASS | after prettier post-regen (`48b6328d`) |
| `make test-unit-tac-validate` | PASS | **870** tests; per-file ≥95% |
| H0c `tests/unit/test_cors_policy.py` | PASS | 6/6 |
| Live HTML in PR CI | PASS | harvest offline-only |

## Fix-in-place (08)

| Issue | Fix |
|-------|-----|
| `membership.py` per-file coverage ~77% | Added harvest write/error-path tests (TC-EV050-001) |
| `membership-check` vs prettier short-array format | `make membership-regen` runs prettier after dump |

## Verdict

**PASS** — proceed 09-qa (delta) → 11-verify-impl.
