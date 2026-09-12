# Verification Report — S011 M6 / T6.1 (08-verify-build)

> **Generated**: 2026-07-14  
> **Scope**: M6 T6.1 — full suite on `evolve/S011-f7-operator-ui` tip  
> **Skill**: 08-verify-build  
> **Session**: S011-f7-operator-ui / EV-008  

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 0 | — | ruff format + prettier |
| Lint (py/js) | PASS | 0 | — | ruff + eslint |
| Typecheck | PASS | 0 | — | basedpyright + tsc |
| Tests — workspace | PASS | 42 | — | pytest |
| Tests — backend | PASS | 1162; cov **98.04%** | — | pytest |
| Tests — auth | PASS | 228 (+31 skip); cov **98.73%** | — | pytest |
| Tests — frontend | PASS | thresholds met (branches gate **88** post ADR-021) | — | vitest |
| Tests — tac2iwxxm | PASS | 100 (+3 skip); cov **95.15%** | — | pytest |
| Tests — iwxxm-validate | PASS | 49; cov **99.67%** | — | pytest |
| Tests — tac-validate / worker | PASS | — | — | pytest |
| Tests — bugs | PASS | 37 (+1 skip) | — | pytest |
| H0c CORS | PASS | 6 | — | `tests/unit/test_cors_policy.py` |
| Connectivity artifacts | PASS | present | — | smoke + verify script |
| Security (secrets) | PASS | 0 | — | gitleaks / `make secrets-check` |
| Integration (compose) | **SKIPPED** | host port 18000/18001 conflicts + Docker disk exhaustion | — | `make test-integration` |

**Overall: PASS** (with integration SKIPPED — host/env blocker, not product defect)

## Fix-in-place (this verify)

| Area | Change |
|------|--------|
| Soft-preview ADR-022 | Layer 1–2 failures no longer hard-abort when `preview=true` (manual/JSON/file); JSON `ConversionRequest.preview` wired |
| Decode coverage | `packages/tac2iwxxm/tests/test_decode_tac.py` restores ≥95% package cov |
| Import fallback stub | `FailedSpan` + `decode_tac` stubs |
| Bug regressions | Admin routes expect **404** (ADR-021); work-session fixtures include `product` |
| Frontend gate | Branch threshold 89→88 after admin-route removal from App coverage surface |

## Connectivity (Stage 08)

- [x] H0c CORS unit tests pass  
- [x] `tests/smoke/test_staging_connectivity.py` present  
- [x] `scripts/deploy/verify_connectivity.sh` present  
- [ ] Compose integration — skipped (ports held by `vecinita-*`; Docker volume ENOSPC)

## Notes

- Tip commits before T6.1: `bdcb9b8` (M1 leftover), `b5b79d7` (S010 mining park).  
- Integration re-run deferred to T6.2/T6.4 when host ports/disk are free, or via CI.
