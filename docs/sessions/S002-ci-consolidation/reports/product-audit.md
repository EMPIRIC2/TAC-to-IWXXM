# Product audit — EV-002 CI consolidation (delta)

**Cycle**: EV-002 / M5  
**Session**: S002-ci-consolidation  
**Date**: 2026-06-22  
**Mode**: delta (CI/pre-commit sections only)

## Consistency check

| Check | Result | Notes |
|-------|--------|-------|
| evolve-decisions ↔ feature-list M5 | ✅ Pass | Job layout and dual-run policy aligned |
| evolve-decisions ↔ test-plan CI/CD | ✅ Pass | validate/test/deploy + pre-commit table match |
| Coverage thresholds | ✅ Pass (documented) | pytest `--cov-fail-under=98` in CI; Codecov 95% per ADR-007 — pre-existing dual gate preserved per R7 |
| Connectivity tiers H4–H5 | ✅ N/A | No browser-facing changes in EV-002 |
| dependency-inventory pre-commit | ⚠️ Stale | Still says "gitleaks + make ci gate" — update in 06-tech-tooling |
| frontend-audit workflow | ⚠️ Stale | Legacy `frontend/` + npm paths; EV-002 merges into validate with pnpm |

## Statement audit (delta scope)

| ID | Statement | Confidence | Verdict |
|----|-----------|------------|---------|
| S1 | PR CI runs ≤3 jobs (validate, test) | High | Auto-approved |
| S2 | Deploy job runs only on push to main | High | Auto-approved (matches current ci-cd.yml) |
| S3 | Pre-commit fast hooks dual-run with CI validate | High | Auto-approved (user R4) |
| S4 | `make ci` remains full local suite entry point | High | Auto-approved |
| S5 | secret-scan + yaml-lint workflows deleted after merge | High | Auto-approved |
| S6 | Frontend npm audit uses pnpm in monorepo validate job | Medium | Approved — replace npm with `pnpm audit` or `pnpm --filter @metar/frontend run audit:ci` |
| S7 | Test job matrix preserves parallel package runs | High | Auto-approved |
| S8 | Integration tests stay in CI test job (not pre-commit) | High | Auto-approved |

## Issues resolved

- **C1**: test-plan metrics table says 95% while CI pytest uses 98% — not introduced by EV-002; R7 explicitly preserves both layers; no doc change required beyond EV-002 table footnote.

## Gate A→B

All Fn (M5) delta specs present; no blocking contradictions. **Gate passed.**
