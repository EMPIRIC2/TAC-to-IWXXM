# PR remediation — PR #684 (PRM-004)

**PR:** https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/684  
**Linked review:** PRR-004  
**Branch:** `evolve/EV-002-ci-consolidation`  
**Date:** 2026-06-23

## Summary

| Metric | Count |
|--------|-------|
| Fixed | 4 |
| Deferred | 0 |
| Won't fix | 0 |
| Commits (local) | 2 |
| CI | not pushed |

## Commits

| SHA | Scope |
|-----|-------|
| `bdc0348` | Blockers F-001 + F-002 — vite lockfile → 6.4.3 |
| `3763192` | Advisories F-003 + F-004 — gitleaks R8 doc + CI step rename |

## Findings

### F-001 / F-002 (blockers)

- **Issue:** `pnpm-lock.yaml` pinned `vite@6.3.5`; `validate-ci` / `audit-frontend` failed (7 advisories).
- **Fix:** `pnpm add -D vite@^6.4.3 --filter @metar/frontend`; audit clean at `--audit-level=low`.
- **Threads:** resolved with replies citing `bdc0348`.

### F-003 (advisory)

- **Issue:** Full-history gitleaks removed with `secret-scan.yml`.
- **Fix:** Documented accepted trade-off as EV-002 **R8** in `docs/decisions/evolve-decisions.md`.
- **Thread:** resolved with reply citing `3763192`.

### F-004 (advisory)

- **Issue:** Step name implied failure-only teardown; `if: always()` runs on success too.
- **Fix:** Renamed to "Stop service stack after integration tests" in `ci-cd.yml`.
- **Thread:** resolved with reply citing `3763192`.

## Review body items (no inline threads)

- No linked issue — not addressed in this cycle.
- Removed test-summary job — not addressed (deploy still gated via `needs: [test]`).

## Next steps

1. Push branch and watch CI (`bash scripts/ci/watch_github_ci.sh evolve/EV-002-ci-consolidation`).
2. Optional: run **18-pr-review** after CI green.
