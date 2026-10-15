# Context — probability on temporary forecast groups

**Session:** `EV-1402-taf-prob-tempo`
**Date:** 2026-10-14
**Mode:** micro evolve
**Ticket:** [#1402](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1402)
**Corpus:** [Corpus: product §F6] [Corpus: product §F20] [Corpus: tests]

## Goal

`PROB30` and `PROB40` stay on the `TEMPO` group they qualify. A probability token that does not qualify a timed temporary group is an error, and its weather is not copied onto the previous forecast.

## Out of scope

- The wording of the info-level `PROB_PRESENT` note
- Multiline splitting
- Other epic children

## Locked decision

The change-group splitter stopped at `TEMPO`, so `PROB40` was left behind and the temporary group was emitted as `TEMPORARY_FLUCTUATIONS`. A `PROB30` token with no `TEMPO` was not a split point, so its weather joined the preceding group. `PROB30 TEMPO` and `PROB40 TEMPO` with a `ddhh/ddhh` period now use the probability temporary indicators. Any other probability shape raises `INVALID_PROB` and is left out of the previous forecast.
