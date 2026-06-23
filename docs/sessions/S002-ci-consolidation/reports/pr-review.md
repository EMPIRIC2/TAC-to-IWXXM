# PR Review — #684 [EV-002] CI consolidation

**Date**: 2026-06-22  
**Reviewer**: 18-pr-review  
**PR**: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/684  
**Verdict**: REQUEST_CHANGES  
**Blockers**: 1  
**Advisories**: 3  

## Summary

Solid CI consolidation (13 jobs → validate/test/deploy) with good Makefile/pre-commit factoring and thorough EV-002 documentation. **Validate job fails** because the new `audit-frontend` gate runs `pnpm audit` against a lockfile still pinning `vite@6.3.5` (7 advisories). Local `make validate-ci` reproduces the same failure; `make validate-fast` passes.

## Blockers

| # | Finding | Location |
|---|---------|----------|
| 1 | Frontend audit gate blocks CI until `pnpm-lock.yaml` resolves vite ≥6.4.3 (package.json already `^6.4.1`) | `Makefile` validate-ci, `apps/frontend/package.json` audit:ci |

## Advisories

| # | Finding | Location |
|---|---------|----------|
| 1 | Deleted `secret-scan.yml` used `fetch-depth: 0` full-history gitleaks; pre-commit gitleaks scans working tree only | `.pre-commit-config.yaml`, deleted workflow |
| 2 | No `Closes #N` / issue link for EV-002 cycle | PR body |
| 3 | Removed `test-summary` / `coverage-enforcement` aggregation — matrix `needs: [test]` still gates deploy, but GHA summary table is gone | `ci-cd.yml` |

## Praise

- Clean validate → test matrix → deploy structure preserving coverage thresholds and integration tests
- `validate-fast` / `validate-ci` Makefile targets align pre-commit with CI validate job
- Pre-commit `make ci` moved to manual stage improves local commit latency

## CI

- Remote: Validate **FAIL** (audit-frontend); Test/Deploy skipped
- Local: `make validate-fast` pass; `make validate-ci` fail (audit)

## Subagents

- Bugbot: could not compute branch diff
- Security review: could not compute branch diff (manual triage performed)
