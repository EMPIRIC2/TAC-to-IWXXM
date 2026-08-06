# 02-verify-plan audit — S046 / EV-038

**Date:** 2026-08-05  
**Mode:** delta · consistency on EV-038 changed sections  
**AC gate:** `D-S046-ac` = 1 (AC1–AC14 approved)  
**Corpus:** `[Corpus: product]` · `[Corpus: tech-spec]` · `[Corpus: api]` · `[Corpus: tests]` ·
`[Corpus: decisions]` · `[docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md]` ·
`[docs/domain/rules/COVERAGE_MATRIX.md]`

## Inventory (delta)

| # | Document | Scope | Status |
|---|----------|-------|--------|
| 1 | feature-list.md | F2/F4/F6/F7/F32 deepen + #846 residual section | audited |
| 2 | test-plan.md | TC-EV038-001..014 + UJ-050 map | audited |
| 3 | user-journeys.md | **UJ-050** added (#854) | audited |
| 4 | evolve-decisions.md §EV-038 | ACs + milestones | audited |
| 5 | 01-requirements-summary.md | AC table approved | audited |
| 6 | COVERAGE_MATRIX / RELEASE_LINE_* | **not yet edited** (07 targets) | consistency note |

Skipped (no delta yet): spec.md, api-contract (unless M2 SoT forces OpenAPI note in 04/07),
deploy.md, dependency-inventory (04 if new deps).

## Consistency checklist

| Check | Result |
|-------|--------|
| AC1–AC14 ↔ TC-EV038-001..014 | ✅ match feature-list / test-plan / evolve-decisions / 01 summary |
| No new Fn | ✅ deepen F2/F4/F6/F7/F32 only |
| #854 UI → UJ + H4–H5 | ✅ **UJ-050** + TC-EV038-007 |
| Milestone order M1→M2→M3→M4 | ✅ D-S046-mplan |
| Spec/API unchanged until M2 SoT | ✅ expected; OpenAPI enum alignment is AC4/07 |
| Domain path-cites | ✅ |
| Live matrix / adopt docs vs AC text | ⚠ **expected lag** until 07 — see S02.M* |

## High confidence (auto-approved)

| ID | Statement | Source |
|----|-----------|--------|
| S1.1 | No new Fn; deepen F2/F4/F6/F7/F32 | Q2=5, AC=1 |
| S1.2 | Milestones M1 docs → M2 release-line → M3 soft → M4 encode | D-S046-mplan Q1=1 |
| S1.3 | Local UI preview at M2/#854 | D-S046-mplan Q2=1 |
| S1.4 | Standard routing includes 04/05/09/10/11/12/13 | Q3=2 |
| S1.5 | AC1–AC14 approved as written | D-S046-ac=1 |
| S1.6 | UJ-050 covers Latest/Previous picker | 02 fix for #854 |

## Medium confidence (user review — recommend accept as 04/07 work)

| ID | Statement | Issue | Recommend |
|----|-----------|-------|-----------|
| S02.M1 | Execution-plan tasks for M1–M4 do not exist yet | Expected — Standard uses **04-tech-plan** | **04:** write milestone task tables |
| S02.M2 | COVERAGE_MATRIX / RELEASE_LINE_* not yet updated for AC1–AC3/AC8–AC13 | 01 text ahead of domain edits | **07:** per-milestone domain edits |
| S02.M3 | OpenAPI / FE SoT artifact (#851) not designed | **RESOLVED** `D-S046-sot`=1 — Python → generated JSON → FE + OpenAPI/CI | **04/07:** implement export + drift CI |
| S02.M4 | Encode ACs (#849/#850/#856) may stay cite-only if no WMO peer | Already in AC text | **07:** implement or document deferral per AC |
| S02.M5 | Deploy 12/13 required by Standard; M1 is docs-only | Per-milestone waive possible | Gate: waive 12/13 for docs-only ship; keep for M2+/runtime |

## Low confidence

| ID | Statement | Note |
|----|-----------|------|
| S02.L1 | #860 translation-failed parity is optional | AC9 allows fixtures **or** deferral — not a hard encode bar |

## Contradictions

None blocking. Prior gap (feature-list promised UJ deepen without journey text) **fixed**
in this audit by adding **UJ-050**.

## Gate A recommendation

**PASS** with S02.M1–M5 accepted as **04/07** work (not 01 doc bugs). Close 02 → start
**04-tech-plan** (Standard; 03 skipped).

## Gate A result (locked)

| ID | Decision |
|----|----------|
| D-S046-02-gate-a | **2** — PASS after SoT decision in 02 |
| D-S046-sot | **1** — Python SoT → generated committed JSON → FE + OpenAPI/CI |

**Status:** Gate A **PASS** 2026-08-05 — close 02 → **04-tech-plan**.
