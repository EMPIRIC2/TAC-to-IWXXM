# QA Report — S020 / EV-015 (F20 delta)

> Generated: 2026-07-22  
> Scope: F20 / F6·F12 deepen (M0–M5 through T5.4)  
> Branch: `evolve/EV-015-aerodrome-quality` @ `ca79381`  
> Mode: evolve delta (09-qa)

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Format | PASS | `make format-check` (T5.4) |
| Lint | PASS | `make lint` ruff + eslint (T5.4) |
| Typecheck | PASS | `make typecheck` basedpyright + tsc (T5.4) |
| Tests (F20 scoped) | PASS | 162 pytest TC-F20-* + 10 Vitest catalog |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` + msgspec high-churn incl. `/lint-issue-catalog` (T5.4) |
| Secrets | SKIPPED | pre-commit detect-secrets PASS on recent commits |
| Staging H4–H5 | ADVISORY | Deferred to T5.7 / 13-deploy-smoke (E15-7 / E15-18) |

**Overall: pass_with_advisories**

## Blocking

None.

## Advisories

1. **QA-H4H5** — Browser connectivity (H4–H5) not exercised in 09; required at 13 per routing plan / E15-14 FE touch.
2. **QA-PIP-AUDIT** — Host-wide `pip-audit` noisy; not treated as F20 gate (same posture as S015).

## Connectivity (stage 09)

| Tier | Result |
|------|--------|
| H0c | PASS |
| H0i (F20 smoke integration) | PASS (`test_tc_f20_005_*`) |
| H4–H5 | pending → 13 |
