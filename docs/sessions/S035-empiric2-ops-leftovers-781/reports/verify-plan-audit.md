# 02-verify-plan audit — EV-028 / S035

**Date**: 2026-08-01  
**Mode**: delta consistency on lean manifest

## Inventory (touched)

| # | Document | Status |
|---|----------|--------|
| 1 | evolve-decisions.md §EV-028 | audited |
| 2 | feature-list.md F12–F14 | audited |
| 3 | deploy.md §PyPI | audited |
| 4 | config-spec.md §F11–F14 | audited |
| 5 | test-plan.md TC-F14-001 + TC-EV028-* | audited |
| 6 | user-journeys.md UJ-023 | boundary check |

## Auto-approved (high confidence)

Derived from D-S035-open / D-S035-routing / E28-*:

| ID | Statement | Verdict |
|----|-----------|---------|
| S1.1 | No new Fn; general cycle deepens F12–F14 publish path | auto-approved |
| S1.2 | Codecov purge + Trusted Publisher EMPIRIC2 + landing READMEs in scope | auto-approved |
| S1.3 | Out: e2e/load secrets, Render rename, Supabase Site URL, #777 publish | auto-approved |
| S1.4 | Lean+build routing; skip 03/05/06/09/11/12 | auto-approved |
| S1.5 | All three packages publish `0.1.1` via OIDC for proof | auto-approved |
| S1.6 | Trusted Publisher fields: EMPIRIC2 / TAC-to-IWXXM / pypi-publish.yml / pypi | auto-approved |
| S1.7 | Public landings must not require ADR/Feature/E10 refs | auto-approved |
| S1.8 | TC-EV028-001..003 cover Codecov, publisher, tag publish | auto-approved |
| S1.9 | Lean Document Manifest 7a | auto-approved |

**Count**: 9 high-confidence auto-approved.

## Consistency checklist (16-evolve)

- [x] F12–F14 acceptance aligned with EMPIRIC2 OIDC + consumer landings
- [x] deploy.md ↔ config-spec.md publisher fields match
- [x] TC-EV028 ↔ evolve-decisions acceptance
- [x] **UJ-023 ↔ TC-EV028-003** — amended 2026-08-01 (`9a` / E28-S2.1): version-generic + EMPIRIC2 + `0.1.1` example
- [x] No browser H4–H5 claimed for this cycle
- [x] #777 publish remains out of scope

## Medium / low for review

| ID | Conf | Category | Statement | Verdict |
|----|------|----------|-----------|---------|
| S2.1 | Medium | Contradiction | UJ-023 vs `0.1.1` proof | **approved 9a** — UJ-023 amended |
| S2.2 | Low | Advisory | Session archive `pypi-bootstrap-token.md` stale owner | **waive** — archive; standing truth deploy.md |

## Gate A

**PASS** 2026-08-01 (`10a`) → 04-tech-plan (Lean skips 03).
