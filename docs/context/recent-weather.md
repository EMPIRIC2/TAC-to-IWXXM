# Context — recent weather

**Session:** `EV-1403-recent-weather`
**Date:** 2026-10-14
**Mode:** micro evolve
**Ticket:** [#1403](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1403)
**Corpus:** [Corpus: product §F6] [Corpus: tests]

## Goal

`RESHRA`, bare `RESH`, and `RETS` encode as recent weather. Bare `RESH` stays showers and is not rewritten to unknown precipitation.

## Out of scope

- Present-weather vicinity groups
- Remarks after `RMK`
- Other epic children

## Locked decision

`RESHRA` and `RETS` already become recent weather. Bare `RESH` was dropped because `SH` is not a complete present-weather token. It is now kept as recent weather `SH`.
