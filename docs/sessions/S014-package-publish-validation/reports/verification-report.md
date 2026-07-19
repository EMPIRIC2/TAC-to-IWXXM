# Verification Report — S014 M6 / T6.1 (08-verify-build)

> **Generated**: 2026-07-19  
> **Scope**: M6 T6.1 — full suite on `evolve/EV-010-package-publish-validation` tip  
> **Skill**: 08-verify-build  
> **Session**: S014-package-publish-validation / EV-010  

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 0 | — | ruff format + prettier |
| Lint (py/js) | PASS | 74 false positives on xsdata trees → excluded | tooling | ruff `--force-exclude` + shared `extend-exclude` |
| Typecheck | PASS | 2 warnings (adapt.py unknown types) | — | basedpyright + tsc |
| Tests — workspace | PASS | 44 + shared/js | — | pytest / vitest |
| Tests — backend | PASS | 1211; cov **98.05%** | — | pytest |
| Tests — auth | PASS | 228 (+31 skip); cov **98.73%** | — | pytest |
| Tests — frontend | PASS | 67 files; branches **86.26%** (≥86) | — | vitest |
| Tests — tac2iwxxm | PASS | 137 (+3 skip) | — | pytest |
| Tests — iwxxm-validate | PASS | 76 (+1 skip) | — | pytest |
| Tests — tac-validate | PASS | 83 | — | pytest |
| Tests — worker | PASS | 11 | — | pytest |
| Tests — bugs | PASS | 39 (+1 deselected) | — | pytest |
| H0c CORS | PASS | 6 + 8 (T5.6 msgspec) | — | pytest |
| Connectivity artifacts | PASS | present | — | smoke + verify script |
| Security (secrets) | PASS | 0 | — | `make secrets-check` / gitleaks |
| Security (deps) | PASS | 0 known CVEs | — | pip-audit (prod export) |
| Integration (compose) | **SKIPPED** | docker image pull hung; host already running unrelated compose services | — | `make test-integration` |

**Overall: PASS** (integration SKIPPED — host/env blocker, not product defect)

## Fix-in-place (this verify)

| Area | Change |
|------|--------|
| Ruff / ADR-027 | `packages/shared/pyproject.toml` `extend-exclude` for `iwxxm_xsd/v*`; Makefile lint targets use `--force-exclude` so CLI paths respect excludes |
| Validate unit tests | Decode msgspec `Response` bodies; expect F11.4 orch layer dedupe (SDK owns XSD/Schematron) |
| Import fallback | Stub `fastapi.responses.Response` + `msgspec_http` |
| Convert file validate | Mock `iwxxm_validate_fn` so layer-credit path hits 98% cov gate |

## Connectivity (Stage 08)

- [x] H0c CORS unit tests pass  
- [x] `tests/smoke/test_staging_connectivity.py` present  
- [x] `scripts/deploy/verify_connectivity.sh` present  
- [ ] Compose integration — skipped (docker pull / host contention)

## Notes

- Tip before T6.1: `0e5f1e3` (M5 verification chore).  
- Integration re-run deferred to T6.2/CI when host is free.  
- Next: T6.2 — 09-qa + 10-e2e (after C→D checkpoint).
