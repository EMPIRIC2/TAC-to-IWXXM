# QA Report — S014 / EV-010 (stage 09-qa, T6.2)

> Generated: 2026-07-19  
> Scope: delta QA for F11–F14 (msgspec HTTP, PyPI packages, Rust validate, xsdata); full lint/format/type/security + H0c re-run; unit suites referenced from T6.1 PASS  
> Branch: `evolve/EV-010-package-publish-validation` (tip includes `d3dbbfb` T6.1)

## Summary

```text
QA Results:
  Lint:           PASS — 0 issues (ruff --force-exclude + eslint --max-warnings 0)
  Format:         PASS — ruff format --check + prettier clean
  Typecheck:      PASS — 0 errors (2 basedpyright warnings in iwxxm_xsd/adapt.py)
  Tests (Python): PASS — T6.1 full suite: backend 1211 @98.05%; auth 228 (+31 skip) @98.73%;
                  tac2iwxxm 137; iwxxm-validate 76; tac-validate 83; worker 11; bugs 39
  Tests (FE):     PASS — T6.1 Vitest 67 files; branches 86.26% (≥86)
  Security:       PASS — gitleaks clean; 0 dangerous pickle/eval/exec in apps+packages;
                  pip-audit: no known vulns (1 ignored — ecdsa / QA-001 carry-forward)
  Cross-file:     generated iwxxm_xsd excluded from lint (ADR-027); template tree OK
  Dependencies:   xsdata / xsdata-pydantic / maturin / msgspec per inventory + ADR-026/027
  Template:       PASS — apps/backend, apps/frontend, apps/worker, packages/*, vendor read-only
  Connectivity:   H0c PASS — 37 CORS-related unit tests (policy + msgspec + config);
                  H0i SKIPPED (compose pull/host — same as T6.1);
                  H4–H5 live Render deferred to 13 — QA-S014-001
```

**Overall: PASS** (advisory QA-S014-001)

## Commands run

```bash
make format-check
make lint
make typecheck
make secrets-check
uv run pytest tests/unit/test_cors_policy.py \
  apps/backend/tests/unit/test_tc_f11_001_cors_after_msgspec.py \
  apps/backend/tests/unit/test_api_cors_config_unit.py -v --no-cov
uv export --format requirements-txt --no-emit-workspace --all-groups -o /tmp/s014-qa-reqs-h.txt
uv run pip-audit -r /tmp/s014-qa-reqs-h.txt --disable-pip $(grep -v '^#' audit/pip-audit-ignore.txt | …)
rg "pickle\.loads|eval\(|exec\(" apps packages --type py
# Full unit matrix: see docs/sessions/S014-…/reports/verification-report.md (T6.1)
```

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-S014-001 | Advisory | H4–H5 / H6′ against Render not re-run in 09 (local CORS + config.json checked; production after msgspec redeploy is T6.5) | Run at 13-deploy-smoke |
| QA-001 | Advisory (carry-forward) | `ecdsa` PYSEC-2026-1325 ignored — HS256-only JWT path | Keep `audit/pip-audit-ignore.txt` |

## Notes

- C→D passed 2026-07-19 (`D-S014-EV010-c-to-d-pass`).
- Local stack smoke (not a substitute for Render H4–H5): frontend `:18000` `config.json` → API `:18001`; OPTIONS preflight for `/api/v1/convert` returns ACAO for `http://127.0.0.1:18000`.
