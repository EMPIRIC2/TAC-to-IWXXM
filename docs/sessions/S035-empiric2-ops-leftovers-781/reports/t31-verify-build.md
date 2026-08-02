# T3.1 — Verify build catch-up (EV-028 / 08-verify-build)

**Date**: 2026-08-01  
**Tip at run**: `3efcb8d`

## Codecov (TC-EV028-001)

| Check | Result |
|-------|--------|
| `codecov` in `.github/workflows`, root README, `apps/backend/README.md` | none |
| `.codecov.yml` | absent |
| `CODECOV_TOKEN` GitHub secret | absent |

## Quality gates (changed package paths)

| Check | Command | Result |
|-------|---------|--------|
| Lint | `make lint-iwxxm-validate lint-tac-validate lint-tac2iwxxm lint-dissemination` | PASS |
| Format | `make format-check` | PASS |
| Typecheck | `make typecheck-py` | PASS |
| Unit — iwxxm-validate | `make test-unit-iwxxm-validate` | **79 passed**, 1 skipped |
| Unit — tac-validate | `make test-unit-tac-validate` | **679 passed** |
| Coverage config | `pytest tests/unit/test_coverage_config.py` | **5 passed** |
| Native — iwxxm-validate | `make test-iwxxm-validate-native` | **15 passed** |
| Native AIXM resolve | `pytest …/test_native_aixm_schema_resolve.py` | **3 passed** |

**Verdict: PASS**
