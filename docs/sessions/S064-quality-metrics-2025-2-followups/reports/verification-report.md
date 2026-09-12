# Verification Report

> Generated: 2026-08-11  
> Scope: EV-055 / S064 — 07 M1–M5 complete → **08-verify-build** Gate C  
> Branch: `evolve/EV-055-quality-metrics-2025-2-followups` @ `333cd694` (+ Gate C fix commit)  
> Corpus: [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13] [Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: adr/ADR-035]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | 0 | 0 | ruff / eslint (`make lint`) |
| Format | PASS | 1 ruff + prettier on test deltas | yes | `make format-check` |
| Typecheck | PASS | 0 errors (pre-existing auth/tac2iwxxm warnings) | — | `make typecheck` |
| Tests (backend) | PASS | 1339 passed; per-file ≥95%; total 98.23% | orchestrator legacy-path tests | `make test-unit-backend` |
| Tests (iwxxm-validate) | PASS | 100 passed, 1 skipped; `c14n.py` 100%; total 99.25% | TC-EV055-003 branch tests | `make test-unit-iwxxm-validate` |
| Tests (frontend) | PASS | 1035 passed, 4 skipped; branches **95.03%** | C14N / page / diff tests | `make test-unit-frontend` |
| H0c CORS | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Integration + smoke | PASS | compose integration + smoke subset | — | `make test-integration` |
| Connectivity artifacts | PASS | present | — | `tests/smoke/test_staging_connectivity.py`, `scripts/deploy/verify_connectivity.sh` |
| Security | PASS | no known vulns; no secret hits in delta paths | — | `uvx pip-audit`; pattern scan |
| Playwright UJ-056 | PASS | 2 passed (TC-EV055-007 deepen) | — | `PLAYWRIGHT_BASE_URL=http://127.0.0.1:18000` local |
| Tip CI | PENDING | CI starts on PR → `stage` | — | GitHub Actions |

**Overall: PASS** (local Gate C). Tip CI watch after draft/open PR to `stage`.

## Fixes during 08

| Issue | Action |
|-------|--------|
| `c14n.py` per-file 69.74% / package 94.92% | Extended TC-EV055-003 (Clark/UUID/href/`_norm_text`) |
| Orchestrator unit tests ignored `schematron_validator` / `xsd_validator` mocks when Rust native-on | `force_legacy_xml_validators`; Schematron submit checks rust-or-validator |
| FE branches 94.26% → below 95 | Extra C14N / page error / unified-diff / display-xml coverage → **95.03%** |
| Format drift on new tests | ruff format + prettier |
| UJ-056 webServer timeout (stale ports / wrong BASE_URL) | Re-run with explicit `127.0.0.1:18000/18001` → **2 passed** |

## Notes

- Live **H4–H5** staging smoke remains stages **12/13**.
- Board #982/#980/#979 stay **In progress** until PR (T5.3).
- Native-first validate path (EV-055) is intentional; legacy lxml unit paths force `rust_available=False`.
