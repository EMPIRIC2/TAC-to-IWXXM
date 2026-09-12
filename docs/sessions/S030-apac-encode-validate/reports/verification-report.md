# 08-verify-build — S030 / EV-023 (T7.2)

**Date**: 2026-07-30  
**Mode**: delta (M0–M7 through T7.1)  
**Branch**: `evolve/EV-023-apac-encode-validate`  
**Tip**: `ae7bdba` (chore sync after `495670b` T7.1)

## Checks

| Check | Result |
|-------|--------|
| `make validate-fast` | PASS |
| EV-023 TC suite (`test_tc_ev023_*` + COLLECT + API smoke) | 70 passed, 7 xfailed, 42 xpassed (informative soft) |
| `packages/tac2iwxxm` full tests | 421 passed, 10 skipped, 7 xfailed, 42 xpassed |
| `make test-unit-dissemination` (≥95% cov) | PASS — 96.36% |
| CORS (`tests/unit/test_cors_policy.py` + backend CORS units) | 38 passed |
| H0i (`apps/backend/tests/integration/test_h0i_connectivity.py`) | 9 passed |

## Connectivity artifacts

| Artifact | Present |
|----------|---------|
| CORS unit policy | yes — `tests/unit/test_cors_policy.py` |
| H0i integration | yes — `apps/backend/tests/integration/test_h0i_connectivity.py` |
| Staging live scripts | deferred to T7.4 / 13 (when_ships) |

## Blocking issues

None.

## Handoff

T7.2 complete → **T7.3** `10-e2e` smoke → T7.4 `13-deploy-smoke` when behavior ships (E23-4).
