# 07-build M4 — Auth UAT (#1006)

**Status:** implementation complete; 08-verify-build **PASS** (2026-08-18)  
**Corpus:** [Corpus: product §F31] [Corpus: product §F21] [Corpus: journeys] [Corpus: tests §TC-EV060-1006]

## Tasks

| ID | Result |
|----|--------|
| T4.1 | Playwright `tc-ev060-1006-auth.e2e.spec.ts` — register stubbed; persist/logout skip without `E2E_USER_*`; guest convert |
| T4.2 | Facilitated UAT-003 on local `:18000` — **ACCEPTED** (`reports/uat-report.md`) |
| T4.3 | Guest convert still works (F21) — same Playwright file + UAT-003 guest step |

## Notes

- No new npm/PyPI deps or auth providers.
- UAT-059..063 deferred to 11-verify-impl / 10-e2e.
- PR #1007 remains open; M4 stacks on the same evolve branch. Promote held.
