# Verification Report

> Generated: 2026-08-17  
> Scope: Lean **08-verify-build** — EV-059 M2 mutation (#874) / PR [#998](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/998)  
> Branch: `evolve/EV-059-ci-schemathesis-mutation` @ `78b0b082`  
> Corpus: [Corpus: tests] [Corpus: product §F34] [Corpus: tech-spec]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Format | PASS | 0 | 0 | ruff format + prettier |
| Lint | PASS | 0 | 0 | ruff + eslint |
| Typecheck | PASS | warnings only (pre-existing) | — | basedpyright + tsc |
| Tests (local `make test-unit`) | PASS | exit 0 | — | pytest matrix |
| H0c CORS | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| CI substantive jobs (PR #998) | PASS | all test/Schemathesis/E2E/Rust green | — | run `32049951760` |
| CI sticky PR comments | **WAIVED** | Quality + Coverage comment jobs 503 | — | `D-S069-ci-comment-waiver` |
| Security (secrets in M2 files) | PASS | none | — | ripgrep |
| pip-audit | SKIPPED / advisory | `pip-audit` not in default env; pin known `pytest-gremlins==1.9.0` | — | `D-S069-m2-pins` |
| Performance | SKIPPED | N/A | — | — |
| Data | SKIPPED | N/A | — | — |

**Overall: PASS** (with CI comment-job waiver + GitHub outage bypass)

## Waivers

| ID | Decision |
|----|----------|
| `D-S069-ci-comment-waiver` | Waive Quality PR comment + Coverage PR comment failures on run `32049951760` (GitHub sticky-comment **503**); substantive jobs green |
| `D-S069-github-outage-bypass` | Bypass GitHub API mutations until user says otherwise; prefer local verification |
| `D-S069-m2-survivors` | 3 equivalent Stryker survivors on `parseCommaSeparatedOrigins` (see `07-build-m2.md`) |

## Connectivity

- Blocking H0c `test_cors_policy.py`: **PASS**
- H4–H5 / staging connectivity: **N/A** (Lean; no UI/deploy this cycle)

## Next

Merge AskQuestion for PR #998 → `stage` (user approval required; GitHub may still flake).
