# QA Report — S015 / EV-011 (F15 delta)

> Generated: 2026-07-20  
> Scope: F15 / F6·F12 deepen (M1–M5 through T5.6)  
> Branch: `evolve/EV-011-metar-lint-quality` @ `53aa185`  
> Mode: evolve delta (09-qa)

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Format | PASS | `make format-check` |
| Lint (F15 Python) | PASS | ruff on catalog/route/registry/tests |
| Lint JS | PASS | `pnpm run lint:js` |
| Typecheck (F15 packages) | PASS_WITH_ADVISORY | `tac-validate` clean; pre-existing `validation.py:79` `Optional[dict]` when file scoped alone (CI backend basedpyright green on prior run) |
| Tests (F15 scoped) | PASS | 61 pytest + 13 Vitest |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` + msgspec high-churn incl. `/lint-issue-catalog` |
| Secrets | SKIPPED | `scripts/check_secrets.sh` not present |
| Staging H4–H5 | ADVISORY | Deferred to T5.10 / 13-deploy-smoke (E11-26) |

**Overall: pass_with_advisories**

## Blocking

None.

## Advisories

1. **QA-H4H5** — Browser connectivity (H4–H5) not exercised in 09; required at 13 per routing plan.
2. **QA-PYRIGHT-DICT** — `apps/backend/src/schemas/validation.py:79` `Optional[dict]` missing type args (pre-F15); out of F15 HARD scope.

## Connectivity (stage 09)

| Tier | Result |
|------|--------|
| H0c | PASS |
| H0i (F15 smoke integration) | PASS (`test_tc_f15_004_*`) |
| H4–H5 | pending → 13 |
