# Evolve summary — EV-050 / S059

**Status:** **completed** — merged to `stage` (`D-S059-merge=1` / `D-S059-close=1`)  
**Date:** 2026-08-09  
**Preset:** Standard (`00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`)  
**Branch:** `evolve/EV-050-codes-wmo-validated`  
**Tip (pre-merge):** `856471fe` · merge `2815ffbe`  
**Tip CI (PR):** [31324484108](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31324484108) SUCCESS  
**PR:** [#964](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/964) **merged** → `stage`  
**Issues:** [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) (closed); [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) already CLOSED (Validated satisfied; residual Present/Cited depth defer+cite in session reports)

## Goal

Ship **Validated** for `#889`: offline harvest from `vendor/schemas/iwxxm-codelists`
(+ pin RDF) and wire `tac-validate` membership so agreed TAC tokens are checked in CI —
no live `codes.wmo.int` HTML in PR CI.

## Delivered

| Area | Evidence |
|------|----------|
| Offline harvest | `scripts/iwxxm/harvest_wmo_membership.py` → `wmo_membership.json`; `make membership-regen` / `membership-check` |
| Membership lint | `UNKNOWN_WMO_MEMBERSHIP` for weather / recent / cloud / SIGMET·AIRMET (+ AIRMET `_` normalize); SpaceWx composed |
| Aggressive fixtures | RE* / AIRMET_ / SpaceWx / TCU accept+negative; AC4 residual defer+cite |
| Dual-profile | `annex3` vs `iwxxm_us` disposition + harness (N/A where unsupported) |
| True-error fix | `REMARK_US_EXTENSION` gated to `iwxxm_us` only |
| Closeout | #882 design-only note; tech-spec harvest path; `D-S059-validated=1` |
| Pre-push / tip CI | AIRMET sad theme `EV050`; E10-21 depth allowlist for AIRMET `EV050` at `full_checklist` |

## Tests

| TC | Result |
|----|--------|
| TC-EV050-001..008 | met (AC4 residuals defer+cite) |
| QA | `make test-unit-tac-validate` (870, ≥95%); `membership-check` PASS |
| Tip CI | SUCCESS on PR tip |

## Decisions (close)

`D-S059-merge=1` · `D-S059-close=1` · `D-S059-11-next=1` · `D-S059-validated=1` ·
`D-S059-route=1` · profiles `1b` · 12/13 waived

## Not done this cycle

- 12/13 staging deploy smoke (waived)
- Promote `stage`→`main` (separate release path)
- Exhaustive Present/Cited register depth / 402 weather (defer+cite)
- Full #882 notification job (design-only shipped)
- Reopen #889 (already closed when merge landed)

## Corpus

[Corpus: product §F6/F12/F15/F20/F23/F24/F28] [Corpus: tests]  
[Corpus: tech-spec] [Corpus: decisions §EV-050]
