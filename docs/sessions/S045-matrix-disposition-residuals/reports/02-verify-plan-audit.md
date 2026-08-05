# 02-verify-plan audit — S045 / EV-037

**Date:** 2026-08-05  
**Mode:** delta · consistency on EV-037 changed sections  
**Commit:** `8cb75d28` (01 docs)  
**Corpus:** `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: decisions]` ·
`[docs/domain/rules/COVERAGE_MATRIX.md]` · `[docs/domain/rules/PROVENANCE_MAP.md]`

## Inventory (delta)

| # | Document | Scope | Status |
|---|----------|-------|--------|
| 1 | feature-list.md | F2 / F6 / F32 deepen + summary rows | audited |
| 2 | test-plan.md | TC-EV037-001..004 | audited |
| 3 | evolve-decisions.md §EV-037 | ACs + dispositions | audited |
| 4 | 01-requirements-summary.md | AC table | audited |
| 5 | COVERAGE_MATRIX / PROVENANCE_MAP | **not yet edited** (07 targets) | consistency note |

Skipped (no delta): spec, user-journeys, api-contract, deploy, deps.

## Consistency checklist

| Check | Result |
|-------|--------|
| AC1–AC4 ↔ TC-EV037-001..004 | ✅ match feature-list / test-plan / evolve-decisions |
| No new Fn | ✅ deepen F2/F6/F32 only |
| No UI → no UJ / H4–H5 N/A | ✅ |
| Spec/API unchanged | ✅ skip OK |
| Domain path-cites | ✅ |
| Live matrix/map vs AC text | ⚠ **expected lag** until 07 — see S02.M* |

## High confidence (auto-approved)

| ID | Statement | Source |
|----|-----------|--------|
| S1.1 | No new Fn; deepen F2/F6/F32 | Q2=1, M1=1, AC=1 |
| S1.2 | VONA SoT hierarchy; Guidance silence non-blocking; cookbook derived | Q2 #869 |
| S1.3 | Official US Schematron = N/A / not published; split validate classes | Q2 #870 |
| S1.4 | AHL source ✅; redesign Bulletin AHL into source vs impl columns | Q2 #872 |
| S1.5 | Close/reword #869/#870/#872 after matrix+TCs; children only for true impl gaps | AC4 |
| S1.6 | H4–H5 N/A; deploy 12/13 waive expected | Q4=1, Lean+07/08 |

## Medium confidence (user review)

| ID | Statement | Issue | Recommend |
|----|-----------|-------|-----------|
| S02.M1 | `US_SCH_ABSENT` / `VONA_GUIDANCE_SILENT` currently status **`gap`** in PROVENANCE_MAP.json | AC2 wants US SCH = **`N/A`**; AC1 wants Guidance silence **non-blocking** (may keep ticket but not encode-block) | **07:** set `US_SCH_ABSENT` → `N/A`; reword `VONA_GUIDANCE_SILENT` to upstream-gap / non-blocking (status `gap` with note OK if TC allows, or `N/A`+ticket) |
| S02.M2 | Eight-family table still has Bulletin AHL **`gap`** for SPECI / VA SIGMET / TCA | AC3: those gaps are **impl**, not source; redesign columns in 07 | **07:** split columns; clear source-missing gaps |
| S02.M3 | TC-EV037 tests do not exist yet under `tests/provenance/` | Expected — Lean tasks in 07 | **07:** add `test_tc_ev037_*.py` |

## Low confidence

| ID | Statement | Note |
|----|-----------|------|
| S02.L1 | Optional combined IWXXM 2025-2 + iwxxm-us 3.0 catalog compat note/canary | Mentioned in research + F2 deepen; **not** a hard AC — defer unless user opts in |

## Contradictions

None blocking between standing specs. Only **spec-vs-live-matrix lag** (01 text ahead of 07 matrix edits) — intentional for Lean.

## Gate A recommendation

**PASS** with S02.M1–M3 accepted as 07 work items (not 01 doc bugs).
