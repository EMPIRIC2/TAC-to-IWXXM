# Evolve summary — EV-035 / S043

**Title:** Rule-source traceability / provenance registry  
**Branch:** `evolve/EV-035-rule-source-traceability`  
**Tip:** `1a1911b9` (+ close commits)  
**Status:** **completed** 2026-08-05  
**Features:** deepen **F6 / F12 / F15 / F2** (no new Fn — G1=2)  
**Preset:** Standard · **Deploy:** waived (S02.L1 / `D-S043-12-13-waive`)

## What shipped

1. Standing **`docs/domain/rules/PROVENANCE_MAP.{md,json}`** — dig ↔ rule ↔ source  
2. CI: **TC-EV035-001..006** (`make test-provenance-quality` — 182 asserts)  
3. Path-filtered pre-commit canary  
4. COVERAGE_MATRIX refresh: VONA ⚠ Guidance + ✅ AHL/FM205; US validate ⚠ #870  
5. Remine residuals ticketed: #869–#872 (#871 closeable)

## Gates

| Gate | Result |
|------|--------|
| A (02) | PASS — Batch A `1,1,1,1` |
| B (04) | PASS — Batch B `1,1,1,1` |
| C→D (08) | PASS |
| 11 | APPROVED (`continue`) |
| Deploy 12/13 | **WAIVED** |

## Corpus cites

`[Corpus: product|tests]` · `[docs/domain/rules/…]` ·  
`[Corpus: WAIVED — domain CORPUS membership; reason: G3=1; decided: EV-035]`

## Follow-ups

- Close or comment [#871](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/871) (TC-EV035-002 green)  
- Keep [#869](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/869) / [#870](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/870) open for upstream residuals  
- [#872](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/872) — bulletin body-split if still needed  
- Open PR → `main` when ready

## Reports

| Artifact | Path |
|----------|------|
| Requirements | `reports/01-requirements-summary.md` |
| Audit | `reports/02-verify-plan-audit.md` |
| Tech plan | `reports/04-tech-plan.md` |
| Execution plan | `reports/execution-plan.md` |
| Gaps | `reports/provenance-gaps.md` |
| 08 | `reports/verification-report.md` |
| 09 | `reports/qa-report.md` |
| 11 | `reports/verify-impl.md` |
