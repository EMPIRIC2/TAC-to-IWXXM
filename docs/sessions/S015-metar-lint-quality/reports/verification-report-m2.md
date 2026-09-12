# 08-verify-build — M2 (S015 / EV-011)

**Date**: 2026-07-20  
**Scope**: Milestone M2 — migrate rule bodies onto registry  
**Branch**: `evolve/EV-011-metar-lint-quality`

## Checks

| Check | Result |
|-------|--------|
| `make test-unit-tac-validate` | PASS — 153 tests |
| `make issue-registry-guard` | PASS (STRICT) |
| `make catalog-check` | PASS |
| Lint / format (tac-validate) | PASS |

## Tasks verified

- T2.1–T2.3 + T2.2a completed
- No `severity=` literals in `rules.py` / `product_rules.py`
- Emissions via `issue_from`

## Next

M3 T3.1 — R1 accept/negative fixtures (station/time/order).
