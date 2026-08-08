# 02-verify-plan — Gate A (S056 / EV-047)

**Date**: 2026-08-08  
**Mode**: delta — M5 husky (#833) + F6 perf (#834) + F7 docs/Help (#956/#957)  
**Status**: Gate A PASS with blocker — `D-S056-gateA=2` (ruleset for perf check before 04)  
**01**: completed (`D-S056-01-ac=1`; UI preview declined `D-S056-ui-preview=2`)

## Inventory (touched)

| # | Document | Delta | Status |
|---|----------|-------|--------|
| 1 | feature-list.md | M5 / F6 / F7 EV-047 AC | audited |
| 2 | user-journeys.md | UJ-054; UJ-DEV-007/008 | audited |
| 3 | test-plan.md | CI/husky EV-047 amend; TC-EV047-001..011 | audited |
| 4 | evolve-decisions / requirements-decisions | EV-047 locks | reference |
| — | spec.md | No component add — F7 frontend + M5 Makefile already map | OK |
| — | api-contract / deploy | N/A unless Help needs new routes (static link expected) | OK |

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — M5 tooling; F6 `packages/tac2iwxxm`; F7 `apps/frontend` Help |
| Feature ↔ Journey | **PASS** — UJ-DEV-007/008 + UJ-054 |
| Journey ↔ Test | **PASS** — → TC-EV047-001..011 |
| Feature ↔ Test | **PASS** — AC1–9 ↔ TC-EV047-* |
| Test ↔ Acceptance | **PASS** |
| Connectivity H4–H5 | **ADVISORY** — UJ-054 browser Help; routing has **10-e2e**; **12/13 waived** — live H4–H5 optional until deploy |
| EV-036 ↔ EV-047 husky | **RESOLVED** — EV-047 explicitly supersedes EV-036 *day-to-day* hook weight; remote CI merge strength retained |

## Statements

### High (auto-approved — D-S056-01-ac=1 / Phase 0 locks)

| ID | Statement | Verdict |
|----|-----------|---------|
| S1.1 | Husky shape A: pre-commit = lint/format only | auto-approved |
| S1.2 | Husky pre-push = fast unit subset only | auto-approved |
| S1.3 | Heavier gates remain CI / opt-in `make` | auto-approved |
| S1.4 | Converter perf: convert-only p95 vs YAML baselines | auto-approved |
| S1.5 | Hard-fail >20% or absolute ceiling; CI required; not husky | auto-approved |
| S1.6 | Product smoke: METAR/SPECI/TAF + thin SIGMET-family; pure-Python first | auto-approved |
| S1.7 | One-pager + handbook under `docs/guides/`; no internal cites | auto-approved |
| S1.8 | README Quick start + in-app Help → one-pager | auto-approved |
| S1.9 | 10-e2e required for UJ-054; 12/13 waived unless 11 needs deploy | auto-approved |

### Medium (user review)

| ID | Statement | Notes |
|----|-----------|-------|
| S2.1 | Exact **fast unit subset** Makefile/pytest target | Not named yet — inventory in 04 (`make test-unit-*` slice). Recommend accept as 04 deliverable. |
| S2.2 | Absolute ms **ceiling** beside 20% | Derive from baselines×1.20 + floor in 04 after first CI noise spike. |
| S2.3 | Perf gate **required check** name / ruleset | Same ops pattern as EV-045: document job `name:`; ruleset may still be empty — docs+script OK; ops apply deferred. |
| S2.4 | Help is **static markdown link** (no new API) | Assumed; if Help needs CMS/route, 04 raises. Recommend accept static. |

### Low

| ID | Statement | Notes |
|----|-----------|-------|
| S3.1 | Printable PDF/HTML for one-pager “if cheap” | Soft AC — markdown that prints to one page is enough; PDF optional in 07. |

## Contradictions

None blocking. EV-036 TC-EV036-001/002 marked historical; TC-EV036-003 remote graph still relevant.

## Gate A recommendation

**PASS** — accept S2.1–S2.4 as 04/07 work; S3.1 optional PDF.

## Gate A decision (`D-S056-gateA=2`)

User chose **option 2**: PASS but **require ruleset update for converter perf check before 04**.

| Item | Locked for 04/07 |
|------|------------------|
| S2.1 | Fast unit subset — 04 inventory |
| S2.2 | Absolute ceiling — 04 from baselines |
| S2.3 | **Blocker** — document + apply required check for perf gate before 04 starts |
| S2.4 | Help = static markdown link |
| S3.1 | PDF optional |

### Locked check name (pending job wire-up in 07; ruleset before 04 may use placeholder)

- `Converter perf (tac2iwxxm)` — exact `jobs.*.name` must match ruleset context (confirm in 04/07)

### Next

1. Inspect current rulesets / permissions  
2. Update `apply_gh_branch_rulesets.sh` (or equivalent) with the perf check context  
3. Apply ruleset (or AskQuestion waive if token lacks admin)  
4. Only then start **04-tech-plan**
