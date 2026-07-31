# 02-verify-plan audit — S033 / EV-026

**Date**: 2026-07-31  
**Mode**: delta  
**Issue**: [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809)

## Scope audited

`feature-list.md` (EV-025 Done + EV-026 deepen) · `user-journeys.md` (UJ-041) ·
`test-plan.md` (TC-EV025-008..009 strict + EV-026 gate) · `requirements-decisions.md` ·
`evolve-decisions.md` §EV-026 · session brief / context

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Journey | **PASS** — F23/F6/F7.g deepen ↔ UJ-041 |
| Journey ↔ Test | **PASS** — UJ-041 ↔ TC-EV025-008..009 (strict EV-026) |
| EV-025 vs EV-026 status | **PASS** — EV-025 Done (soft); EV-026 In progress (equality) |
| TC id reuse | **PASS** — E26-TC=1 documented in test-plan + UJ-041 |
| ADR-032 policy | **PASS** — wmoPass only under canonicalize equality |
| Out of scope | **PASS** — #738 / US REMARKS reopen excluded |
| Cross-doc naming | **PASS** — VolcanicAshSIGMET / wmoPass / sigmet-multi-location-VA |
| Spec/Config/API skipped | **PASS** — lean manifest; no contract surface |

## Auto-approved (high confidence) — 12

Derived from D-S033-open / E26-* / corpus deltas already locked:

1. #809 residual is equality + catalog promote only
2. Soft path shipped in #816; do not re-litigate soft green
3. Reuse TC-EV025-008..009 with strict semantics
4. Catalog flip `wmoReference` → `wmoPass` when equality holds
5. FIXTURE_GAPS equality-pending cleared on promote
6. No new Fn; deepen F23/F6/F7.g
7. Lean+build routing; skip 03/05/06/09/11/12
8. UI N/A (catalog/Vitest only)
9. #738 out of scope
10. US REMARKS (#810–#812) not reopened
11. Root remains `iwxxm:VolcanicAshSIGMET`
12. 13-deploy-smoke only when ships

## Medium confidence (Batch F — locked)

| ID | Statement | Decision |
|----|-----------|----------|
| S02.M1 | Encoder may use example-specific calendar / ATS-MWO stamps (as other WMO stems) to reach ADR-032 equality without changing default convert API | **1** Approve — `D-S033-EV026-s02m1-1` |
| S02.M2 | Ring vertex order + coordinate formatting may normalize toward vendor canonical shape for this stem only (not a global GML policy change) | **1** Approve — `D-S033-EV026-s02m2-1` |
| S02.L1 | No new UJ id — deepen UJ-041 only; UJ-039 sample-menu listing stays | **1** Approve — `D-S033-EV026-s02l1-1` |

## Gate A

**PASS** (`D-S033-02-phase-a`) — Batch F 1,1,1; Lean → **04-tech-plan**.
