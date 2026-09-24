# Context — lettered SIGMET and AIRMET bulletin sequence

**Session:** `EV-1279-lettered-sequence`
**Date:** 2026-09-24
**Mode:** full evolve
**Ticket:** [#1279](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1279)
**Corpus:** [Corpus: product §F6] [Corpus: system-spec] [Corpus: tests]

## Goal

Split a SIGMET or AIRMET bulletin whose sequence is a letter plus digits (`A02`, `E01`). The single-report parser already accepts that form. The bulletin splitter only accepts digits.

## Out of scope

- US convective SIGMET ([#1267](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1267)).
- Changing the IWXXM sequence element beyond what the parser already emits.
- G-AIRMET, US VONA, and Canadian SIGMET.
- Browser UI, connectivity tiers H4–H5, and a deploy. Do not promote `stage` to `main`.

## Locked intake

| Topic | Lock |
|-------|------|
| Scale | Full. Spec→Build gate **closed** until documenting verify |
| Session | Feature, normal urgency, `EV-1279-lettered-sequence` |
| Users | Maintainers splitting multi-report SIGMET and AIRMET bulletins |
| Fence | Digits-only sequences such as `SIGMET 3` keep the current split. No HTTP change. No PII |
| Docs | Delta `docs/feature-list.md` and `docs/test-plan.md`. Waive a new CORPUS row |
| Build intent | `packages/tac2iwxxm` bulletin split and tests. Pull request into `stage` |
| Live sample | One Aviation Weather Center bulletin when a lettered sequence is published. If none is present, fixtures cover the three checks and the live pass says it was not sampled |
| Memory | No accepted knowledge for this query. Historical hit `q-verification-gate` (vecinita) **waived** |

## Problem

`packages/tac2iwxxm/src/tac2iwxxm/bulletin.py` matches a SIGMET or AIRMET body with `SIGMET\s+\d+` and `AIRMET\s+\d+`. A report line `YMMM SIGMET A02 VALID …` does not match, so the bulletin does not split. The single-report parser in `slot_builders/sigmet_airmet.py` already accepts a letter plus digits (`A02`) and a phonetic form (`ALPHA 02`) in `_parse_sequence_token`.

## Inventory

| Piece | State |
|-------|--------|
| Bulletin SIGMET/AIRMET patterns | Digits only (`bulletin.py` `_TAC_SIGMET`, `_TAC_AIRMET`) |
| Single-report sequence | Lettered and digits (`_parse_sequence_token`) |
| Convective SIGMET | Separate grammar. Out of this cycle |
| UI / HTTP | Unchanged |

## Resolutions

| ID | Decision |
|----|----------|
| R1 | Widen the bulletin sequence to the letter-plus-digits form the parser already accepts |
| R2 | Keep digits-only sequences on the current path |
| R3 | H4–H5 and UI are N/A |
| R4 | Live sample is best-effort against Aviation Weather Center; a missing lettered bulletin does not fail the checked-in tests |
