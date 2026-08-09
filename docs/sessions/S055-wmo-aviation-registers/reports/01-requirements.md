# 01-requirements — S055 / EV-046

**Mode:** delta (Lean)  
**Date:** 2026-08-08  
**Issue:** [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889)  
**Corpus:** [Corpus: product] [Corpus: tests] [Corpus: decisions]

## Phase 0 lock (recorded)

| ID | Choice | Meaning |
|----|--------|---------|
| D-S055-families | 3 | Full F6 product-family coverage % |
| D-S055-validated | 1 | Waive Validated for Lean; Standard follow-on |
| D-S055-cite | 2 | Domain docs + ISSUE_CATALOG / provenance URIs |
| D-S055-phase01 | 1 | Proceed 01 |

## Document manifest (delta)

| Document | Action |
|----------|--------|
| `docs/decisions/evolve-decisions.md` §EV-046 | Scope + AC1–AC6 |
| `docs/feature-list.md` | Summary rows + deepen block |
| `docs/test-plan.md` | TC-EV046-001..006 + verify gate |
| Domain RULE_SOURCE_URLS / COVERAGE_MATRIX / mining / ISSUE_CATALOG | Deferred to post-01 Lean deliverable work (after Gate A) |
| User journeys / API / deploy | N/A — no UI/API/deploy |

## UI preview

N/A — no browser UI (`D-S055-open=2`).

## AC confirmation

**`D-S055-01-ac=1`** — AC1–AC6 confirmed as written; 01 closed → 02-verify-plan.

## Exit

- [x] Scope locked (Phase 0)
- [x] Feature-list deepen + evolve-decisions ACs
- [x] Test-plan TC-EV046-001..006
- [x] No new Fn; UI N/A
- [x] Hand off 02-verify-plan
