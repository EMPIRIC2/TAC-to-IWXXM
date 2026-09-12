# 02-verify-plan audit — S015 / EV-011

**Date**: 2026-07-19  
**Mode**: delta (F15 + F6/F12 deepen + SPECI adjacency)  
**Status**: **PASS** (medium verdicts 2026-07-19)

## Document inventory

| # | Document | Delta scope | Status |
|---|----------|-------------|--------|
| 1 | feature-list.md | F15 + F6/F12 deepen notes; F11–F14 status sync | audited |
| 2 | spec.md | tac-validate F15 registry delta | audited |
| 3 | user-journeys.md | UJ-024 METAR/SPECI | audited |
| 4 | test-plan.md | TC-F15-001..005 | audited |
| 5 | api-contract.md | lint-tac wire shape unchanged | audited |
| 6 | ADR-028 | Issue registry | audited |
| 7 | COVERAGE_MATRIX.md | METAR row S015 note | audited |
| 8 | metar-research-catalog.md | R1–R8 themes | audited |
| 9 | config-spec / env / deploy | No new env expected | N/A (skip unless 04 finds knobs) |

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — F15 → tac-validate registry + ADR-028 |
| Feature ↔ Journey | **PASS** — F15 → UJ-024 |
| Journey ↔ Test | **PASS** — UJ-024 → TC-F15-001..005 |
| Feature ↔ Test | **PASS** — F15 acceptance ↔ TC-F15 gate |
| Spec ↔ API | **PASS** — wire shape unchanged; codes from registry |
| Spec ↔ Config | **N/A** — no new env knobs in 01 |
| Cross-doc naming | **FIXED** — F15 title/matrix include SPECI; F11–F14 detail status → Implemented (matched summary) |
| Scope boundaries | **PASS** — FMS excluded; F7 stays Planned; #732 METAR focus + SPECI adjacency |
| Connectivity H4–H5 | **PASS** — TC-F15-004 / F15 gate require H4–H5 if FE redeploy |

## Auto-approved (high confidence)

| ID | Statement | Source |
|----|-----------|--------|
| S1.1 | F15 Planned; registry in `tac-validate` + docs catalog | E11-8, E11-9 |
| S1.2 | Severities `info` \| `warning` \| `error`; stable public codes | E11-10, ADR-028 |
| S1.3 | Full #732 + max research/expansion R1–R8 | E11-3, E11-6, E11-13 |
| S1.4 | Deepen F6/F12; new Fn F15 only | E11-4 |
| S1.5 | F7 remains Planned; smoke under F15 | E11-11 |
| S1.6 | lint-tac HTTP wire shape unchanged | E11-12 |
| S1.7 | SPECI adjacency explicit (UJ-024, TC-F15-005) | E11-13 |
| S1.8 | Routing 00–13 incl. 03/06 + Render | E11-5 |
| S2.1 | Spec §tac-validate F15 delta matches ADR-028 | E11-8 |
| S3.1 | UJ-024 covers METAR + SPECI operator + CI steps | E11-13 |
| S4.1 | TC-F15-001..005 cover registry, goldens, negatives, smoke, adjacency | E11-13 |
| S5.1 | api-contract documents no new response fields | E11-12 |

**Auto-approved: 12** high-confidence statements.

## Fix-in-place (no user verdict needed)

| Issue | Fix |
|-------|-----|
| F11–F14 detail sections still said Planned while summary said Implemented | Updated detail **Status** → Implemented (EV-010 close leftover) |
| F15 matrix/title said METAR-only after E11-13 SPECI | Retitled / matrix → METAR/SPECI |

## Medium / low — need user verdict

### S1.M1 `[Ambiguity]` — F15 title vs GitHub #732 METAR-only framing

**Statement**: Issue #732 is titled/scoped as METAR product quality; EV-011 now explicitly includes SPECI adjacency and SPECI goldens/negatives.  
**Risk**: Sibling SPECI quality ticket (if any) may overlap; or #732 commenters expect METAR-only.

**Options**:
1. **Keep METAR+#SPECI adjacency in F15** (recommended — matches E11-13); note on #732 that SPECI shares METAR/SPECI pack
2. **METAR-only fixtures this cycle**; SPECI adjacency = Auto-detect/product-hint tests only (no SPECI golden expansion)
3. Let me explain / provide more context

### S1.M2 `[Uncertainty]` — Max expansion deliverability

**Statement**: Aggressive encode R1–R8 + opportunistic improvements in one cycle  
**Confidence**: High that user requested it (E11-6); Medium that every theme ships fully without deferrals  
**Options**:
1. **Keep max scope**; 04 milestones with AskQuestion kill-switch if blocked (recommended)
2. **Tier themes now**: must-ship registry+R6 goldens+SPECI adjacency; R1–R5/R8 stretch
3. Let me explain / provide more context

### S9.M1 `[Gap]` — plan-tooling / CORPUS scope line

**Statement**: CORPUS product row still says “Scope (F1–F4 / M1–M6)” — outdated vs F15  
**Options**:
1. **Fix CORPUS product blurb to F1–F15 / M1–M6** in this 02 pass (recommended)
2. Defer CORPUS wording to 03-plan-tooling
3. Let me explain / provide more context

## Contradictions found

None blocking after F11–F14 status sync and F15 SPECI naming fix.

## Medium verdicts (2026-07-19)

| Item | Verdict |
|------|---------|
| S1.M1 #732 vs SPECI | **1** — Keep METAR+SPECI in F15; note on #732 that SPECI shares pack |
| S1.M2 max expansion | **1** — Keep max scope; 04 milestones + AskQuestion kill-switch |
| S9.M1 CORPUS blurb | **1** — Fixed to F1–F15 / M1–M6 |

## Overall

**PASS** — 02-verify-plan complete. Next: **03-plan-tooling** (registry guardrails); A→B gate after 03.
