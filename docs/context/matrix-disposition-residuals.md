# Scoped context — matrix-disposition-residuals (S045 / EV-037)

**Date:** 2026-08-05  
**Session:** S045-matrix-disposition-residuals  
**Cycle:** EV-037  
**Issues:** [#869](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/869), [#870](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/870), [#872](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/872)  
**Epic:** [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)

## Problem

EV-035 remine left three open documentation/matrix residuals. Agent research (2026-08-05)
concluded they are disposition/matrix problems, not missing encode engines.

## Locked dispositions

1. **#869 VONA** — Guidance silence is a non-blocking upstream gap. Conversion SoT =
   ICAO + WMO FM205 + AHL + `vona.xsd` + WMO `iwxxm.sch` + code lists; cookbook is derived.
2. **#870 IWXXM-US** — Official US Schematron artifact = **N/A / not published**. Do not
   mark all US validation N/A; split WMO XSD/SCH, US XSD, semantic rules, fixtures.
3. **#872 Bulletin AHL** — WMO AHL publication covers all relevant `T1T2` families. Mark
   source ✅; track parser/BBB/splitter/filename/COLLECT/fixtures/CI separately; children
   only for true implementation gaps.

## Primary artifacts

| Artifact | Role |
|----------|------|
| `docs/domain/rules/COVERAGE_MATRIX.md` | Family × convert/validate/AHL cells |
| `docs/domain/rules/PROVENANCE_MAP.md` (+ `.json`) | Cite provenance |
| `docs/sessions/S043-…/reports/provenance-gaps.md` | Prior remine residual log |
| `tests/provenance/` | TC-EV035-* canaries — extend or add TC-EV037-* |

## Corpus cites

- `[Corpus: product]` — deepen F2 / F6 / F32 (no new Fn)
- `[Corpus: tests]` — provenance / matrix TCs
- `[Corpus: decisions]` — evolve-decisions EV-037
- `[docs/domain/rules/COVERAGE_MATRIX.md]`
- `[docs/domain/rules/PROVENANCE_MAP.md]`

## Out of scope

Product UI, deploy, inventing US Schematron, editing upstream Guidance, full AHL impl
beyond matrix redesign + residual child tickets.
