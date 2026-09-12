# 01-requirements summary — S045 / EV-037

**Date:** 2026-08-05  
**Mode:** delta · deepen F2 / F6 / F32 · no new Fn · no UI  
**Manifest:** M1=1 — Feature List + Test Plan + ACs + matrix/provenance targets  
**Corpus:** `[Corpus: product]` · `[Corpus: tests]` · `[Corpus: decisions]` ·
`[docs/domain/rules/COVERAGE_MATRIX.md]` · `[docs/domain/rules/PROVENANCE_MAP.md]`

## Interview plan (approved)

| Doc | Action |
|-----|--------|
| Feature List | Deepen F2 (#870), F6 (#872), F32 (#869) — **written** |
| Test Plan | TC-EV037-001..004 — **written** |
| Spec / API / UJ / Deploy / Deps / ADR | **Skipped** (no runtime / no UI) |
| COVERAGE_MATRIX / PROVENANCE_MAP | Spec targets for **07-build** (not edited in 01) |

## Acceptance criteria (EV-037)

| ID | Criterion | Ticket | TC |
|----|-----------|--------|-----|
| AC1 | VONA SoT hierarchy documented; Guidance silence non-blocking ⚠; cookbook = derived | #869 | TC-EV037-001 |
| AC2 | US Schematron = N/A/not published; validate classes split; do not N/A all US validation | #870 | TC-EV037-002 |
| AC3 | AHL source ✅ all mapped families; Bulletin AHL cell → source vs impl columns; children only for true impl gaps | #872 | TC-EV037-003 |
| AC4 | GitHub #869/#870/#872 closed or reworded per dispositions; epic #846 linked | all | TC-EV037-004 |

## 07-build targets (from ACs)

1. Update `docs/domain/rules/COVERAGE_MATRIX.md` — VONA convert cell, METAR_US validate split, eight-family AHL column redesign
2. Update `docs/domain/rules/PROVENANCE_MAP.md` (+ `.json`) — `VONA_GUIDANCE_SILENT`, `US_SCH_ABSENT`, AHL source rows
3. Add/extend `tests/provenance/` asserts for TC-EV037-001..003
4. Close or comment #869/#870/#872; open #872 children only if needed

## Out of scope

Upstream Guidance edit · invent US Schematron · product UI · deploy · full AHL impl packs
