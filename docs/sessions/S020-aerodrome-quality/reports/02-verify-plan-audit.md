# 02-verify-plan audit — S020 / EV-015

**Date**: 2026-07-22  
**Mode**: delta (F20 + F6.b/F6.c/F12 deepen + #735/#734)  
**Status**: **PASS** (medium verdicts 2026-07-22)

## Document inventory

| # | Document | Delta scope | Status |
|---|----------|-------------|--------|
| 1 | feature-list.md | F20 Planned + F6/F12 deepen | audited |
| 2 | spec.md | F20 + tac2iwxxm/tac-validate deltas; F16–F19 status sync | audited |
| 3 | user-journeys.md | UJ-031 | audited |
| 4 | test-plan.md | TC-F20-001..006 | audited |
| 5 | api-contract.md | Full endpoint review; no wire breaks | audited |
| 6 | COVERAGE_MATRIX.md | TAF/SPECI F20 themes T1–T4 / S1–S3 / C1 | audited |
| 7 | ADR | ADR-028 reuse (no new ADR) | N/A |
| 8 | plan-adherence.mdc | F20 + F16–F19 Done | audited |

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — F20 → tac-validate/tac2iwxxm + F20 section |
| Feature ↔ Journey | **PASS** — F20 → UJ-031 |
| Journey ↔ Test | **PASS** — UJ-031 → TC-F20-001..006 |
| Feature ↔ Test | **PASS** — F20 acceptance ↔ TC-F20 gate |
| Spec ↔ API | **PASS** — no new routes; product enum already has taf/speci |
| Spec ↔ Config | **N/A** — no new env knobs |
| Cross-doc naming | **FIXED** — spec F16–F19 **Planned** → **Done** (matched feature-list / EV-014 close) |
| Scope boundaries | **PASS** — siblings OOS; F7 Planned; PyPI OOS |
| Connectivity H4–H5 | **PASS** — TC-F20-005 / E15-7 |

## Auto-approved (high confidence)

| ID | Statement | Source |
|----|-----------|--------|
| S1.1 | F20 Planned; TAF+#735 + SPECI+#734 full bars | E15-2, E15-3, E15-5 |
| S1.2 | Deepen F6.b/F6.c + F12; ADR-028 reuse | E15-3 |
| S1.3 | Lean+build routing (skip 03/05/06/12) | E15-route-amend=A |
| S1.4 | F7 remains Planned; smoke under F20 | E15-6 |
| S1.5 | No PyPI bump; siblings OOS; no F16–F19 changes | E15-6 |
| S1.6 | H1–H3 if API; H4–H5 when FE | E15-7 |
| S1.7 | UJ-031 + TC-F20-001..006 | E15-8 / manifest B |
| S1.8 | API wire unchanged; full endpoint review | E15-9=B / EV-015/F20-R8 |
| S2.1 | Spec F20 exceptional-rule lists match #735/#734 | E15-5 |
| S3.1 | UJ-031 covers TAF + SPECI operator + CI | E15-2 |
| S4.1 | Matrix themes T1–T4 / S1–S3 / C1 are HARD (defer via AskQuestion) | E15-5 |
| S5.1 | No new HTTP routes for F20 | E15-9 |

**Auto-approved: 12** high-confidence statements.

## Fix-in-place (no user verdict needed)

| Issue | Fix |
|-------|-----|
| `spec.md` still labeled F16–F19 **Planned** after EV-014 Done | Updated component overview, backend bullets, frontend, and §F16–F19 → **Done** |

## Medium / low — verdicts (2026-07-22)

### S1.M1 `[Uncertainty]` — Full theme deliverability under Lean+build

**Verdict**: **1 — Approve** keep full HARD themes; 04 milestones with AskQuestion kill-switch  
**Decision id**: `D-S020-EV015-s1m1-1`

### S1.M2 `[Ambiguity]` — Session slug vs full SPECI scope

**Verdict**: **2 — Rename** to `S020-aerodrome-quality` / `evolve/EV-015-aerodrome-quality`  
**Decision id**: `D-S020-EV015-s1m2-2`  
**Done**: session dir, context brief, git branch renamed; standing-doc refs updated; E15-1 amended.

### S9.M1 `[Uncertainty]` — Skip 05-verify-tech

**Verdict**: **1 — Keep skip 05**; lightweight consistency pass at 04 exit  
**Decision id**: `D-S020-EV015-s9m1-1`

## Gate result

**02-verify-plan: PASS** — consistency OK; medium items resolved; ready for Phase A checkpoint → 04-tech-plan.

### Historical options (pre-verdict)

### S1.M1 `[Uncertainty]` — Full theme deliverability under Lean+build

**Statement**: Close all matrix themes T1–T4 / S1–S3 / C1 this cycle (or explicit deferrals).  
**Confidence**: High that user requested full depth (E15-5); Medium that every theme ships without stretch under Lean+build (no 05/03).

**Options**:
1. **Keep full HARD themes**; 04 milestones with AskQuestion kill-switch if blocked *(recommended — mirrors EV-011 S1.M2)*
2. **Tier now**: must-ship T1+T4+S2+S3 (+ C1 common); T2/T3/S1 stretch
3. Let me explain / provide more context

### S1.M2 `[Ambiguity]` — Session slug `taf-quality` vs full SPECI scope

**Statement**: Session id / branch emphasize TAF; scope is TAF **and** full SPECI (#734).  
**Risk**: Issue/PR titles may under-signal SPECI.

**Options**:
1. **Keep slug** `S020-taf-quality` / `evolve/EV-015-taf-quality`; titles/PRs say “TAF + SPECI”
2. **Rename** session/branch to `aerodrome-quality` / similar (git rename) ← **chosen**
3. Let me explain / provide more context

### S9.M1 `[Uncertainty]` — Skip 05-verify-tech

**Statement**: Lean+build skips 05; execution plan from 04 goes straight toward build.  
**Risk**: Tech contradictions caught late.

**Options**:
1. **Keep skip 05**; run a lightweight consistency pass inside 04 exit *(recommended)* ← **chosen**
2. **Re-add 05-verify-tech** to routing now
3. Let me explain / provide more context
