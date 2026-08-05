# Evolve summary — EV-037 / S045

**Title:** Matrix dispositions #869 / #870 / #872  
**Branch:** `evolve/EV-037-matrix-disposition-residuals`  
**Status:** **completed** 2026-08-05 — PR [#887](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/887) MERGED @ `b7302fe4`  
**Features:** deepen **F2 / F6 / F32** only (no new Fn)  
**Preset:** Lean+07/08 · **Deploy:** waived (`D-S045-12-13-waive`)  
**Verify:** 08 PASS @ `90c2e8a3` · provenance quality **188** passed · CI [31049365217](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31049365217) SUCCESS

## What shipped

1. **#869** — VONA SoT hierarchy; Guidance silence non-blocking; cookbook = derived  
2. **#870** — Official US Schematron = N/A/not published; validate class split retained  
3. **#872** — AHL source ✅; Bulletin AHL source vs impl columns  
4. **Provenance** — `VONA_GUIDANCE_SILENT` / `US_SCH_ABSENT` → N/A; gaps[] empty  
5. **Tests** — `tests/provenance/test_tc_ev037_dispositions.py` (TC-EV037-001..004)  
6. **Issues** — #869 / #870 / #872 **closed** (epic #846)

## Gates

| Gate | Result |
|------|--------|
| A (02) | PASS (`D-S045-02-gate-a`) |
| B→C | waived_lean |
| C→D / 11 | **APPROVED** (`D-S045-11`) |
| Deploy 12/13 | **WAIVED** (`D-S045-12-13-waive`) |

## Corpus cites

`[Corpus: product]` F2/F6/F32 · `[Corpus: tests]` · `[Corpus: decisions]` EV-037 ·  
`[docs/domain/rules/COVERAGE_MATRIX.md]` · `[docs/domain/rules/PROVENANCE_MAP.md]`

## Reports

| Artifact | Path |
|----------|------|
| Requirements | `reports/01-requirements-summary.md` |
| Audit | `reports/02-verify-plan-audit.md` |
| 07 | `reports/07-build-report.md` |
| 08 | `reports/verification-report.md` |
| 11 | `reports/verify-impl.md` |
| Gaps | `reports/provenance-gaps.md` |
