# #889 Validated closeout — AC5 / TC-EV050-005

> **Cycle**: EV-050 / S059 · **Task**: T4.2 · **Decision**: `D-S059-validated=1`  
> **Corpus**: [Corpus: decisions §EV-050], [Corpus: product §F12/F15], [Corpus: tests]

## Verdict

**#889 Validated triad element: SATISFIED** (not re-scoped).

Lean cycle EV-046 waived Validated (`D-S055-validated=1`) and filed
[#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959). This Standard cycle closes that
waiver with offline harvest + `tac-validate` membership CI.

## Close criteria checklist

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Standing offline harvest from vendor codelists (+ pin RDF) | Met | `tac_validate.membership` / `wmo_membership.json` |
| 2 | Happy + unknown/sad membership for v1 families | Met | TC-EV050-002 matrix |
| 3 | Harvest cadence documented vs `iwxxm-codelists` pin | Met | tech-spec + TAC_VALIDATION + RULE_SOURCE_URLS |
| 4 | Aggressive fixture gaps closed or defer+cite | Met | `fixture-coverage-delta-t2.4.md` |
| 5 | No live `codes.wmo.int` HTML in PR CI | Met | harvest/Makefile offline-only |
| 6 | Dual-profile + true-error bar (cycle amend) | Met | disposition + REMARK_US_EXTENSION gating |
| 7 | #882 notify pipeline | N/A for Validated | AC6 design-only note |

Standing log: [evolve-decisions.md](../../../decisions/evolve-decisions.md) §EV-050 M4/AC5.

## Issue process

| Issue | Action at T4.2 | After PR → `stage` |
|-------|----------------|--------------------|
| [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) | Comment close criteria + tip SHA | Close when merge lands |
| [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) | Comment Validated **satisfied**; residuals remain Present/Cited depth | Leave open unless maintainers close Validated-only |
| [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) | Pointer to design note only | Remains open (spike) |
| [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) | Unchanged compose | Remains open |
