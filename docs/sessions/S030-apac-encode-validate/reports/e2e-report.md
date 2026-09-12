# 10-e2e smoke — S030 / EV-023 (T7.3)

**Date**: 2026-07-30  
**Mode**: smoke (Lean+build; **E23-ui = N/A** — engine + goldens, no FE workbench delta)  
**Branch**: `evolve/EV-023-apac-encode-validate`

## Mechanism

| Signal | Choice |
|--------|--------|
| Cycle UI | None (engine packages + thin API Form flag) |
| Mechanism | Library + in-process HTTP (TestClient) |
| Browser MCP | **N/A** this cycle |

## Tier results

| Tier | Scope | Result |
|------|-------|--------|
| **T0** | Package TC-EV023-001..009 + FIR/COLLECT helpers | PASS (informative suite soft/xfail) |
| **T0** | API smoke `test_tc_ev023_010_api_smoke.py` (convert gate + NSC + validate) | PASS (3) |
| **T1** | H0i connectivity | PASS (9) — recorded in 08 verification-report |
| **T2** | Staging H1–H5 | Deferred to **T7.4 / 13-deploy-smoke** (E23-4 when_ships) |
| **T3** | Live browser UJ | N/A — no UI delta; 11 optional |

## Journeys deepened (no new UJ)

| Journey | Smoke evidence |
|---------|----------------|
| UJ-001 / convert | API convert smoke + package goldens |
| UJ-005 / validate | API validate on NSC convert XML |
| UJ-006 / lint | Package lint/SCH negatives from P0 (prior M1–M3) |

## Blocking

None for smoke scope.

## Handoff

T7.3 complete → **T7.4** `13-deploy-smoke` after PR merge/deploy when convert/validate behavior ships (E23-4). Optional **11-verify-impl** skipped unless requested.
