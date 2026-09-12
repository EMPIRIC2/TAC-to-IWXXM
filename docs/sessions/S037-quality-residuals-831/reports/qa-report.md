# QA Report — S037 / EV-030 (T4.2 / 09-qa delta)

> Generated: 2026-08-03  
> Scope: Delta QA for F29 + #829/#820 deepen (UJ-044)  
> Branch: `evolve/EV-030-quality-residuals-831` @ `1f47eb5`  
> Mode: evolve delta (not full-repo remediating QA)

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Format / lint / typecheck / secrets | PASS | `make validate-fast` (T4.1) |
| Quality matrices PR smoke | PASS | `make test-quality-matrices-smoke` — 50 passed / 1900 deselected |
| tac2iwxxm unit + cov | PASS | 740 passed; **cov 95.05%** (≥95) |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` — 6 passed |
| H0i integration | PASS (local) | 6 passed / 9 skipped (Docker/live not required for delta) |
| GitHub CI | PASS | [run 30823368642](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30823368642) |
| H4–H5 staging browser | ADVISORY → T4.4 | Required at 13-deploy-smoke (E30-T6; FE unlock shipped; `D-S037-ui-preview=2`) |

**Overall: pass_with_advisories** (H4–H5 deferred to T4.4)

## Feature / journey coverage (delta)

| Item | Status |
|------|--------|
| F29 harness (METAR/SPECI pilot) | PASS — smoke green |
| #829 TC SIGMET + A6-2-TC catalog | PASS — closed; child #835 |
| #820 VAA/TCA decode residuals | PASS — official peers empty |
| UJ-044 T0 | PASS — matrices + EV030 TCs |

## Advisories

1. **H4–H5** — live browser connectivity for FE catalog unlock deferred to **T4.4 / 13-deploy-smoke**
2. **Semver** — `tac2iwxxm` **0.2.4** (`D-S037-semver-tac2iwxxm=2`); no PyPI tag this cycle unless asked
3. Integration live skips — expected without Docker stack in this delta run

## Blocking findings

None.
