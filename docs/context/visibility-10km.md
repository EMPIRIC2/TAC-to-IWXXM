# Context: 10 km visibility

**Session:** `EV-1406-visibility-10km`
**Date:** 2026-10-16
**Mode:** micro evolve
**Ticket:** [#1406](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1406)
**Corpus:** [Corpus: product §F6] [Corpus: tests]

## Goal

Encode `1 1/2SM` as about 2400 m. Use one 10 km rule for `9999` and `10SM` on METAR and on TAF.

## Out of scope

- Remark visibility such as `VIS16KM`
- Unobserved `////` visibility
- QNH when an altimeter setting is also present
- METAR variable wind, impossible days, and the remarks policy

## Locked decision

A mixed statute-mile group uses the existing fraction parser. `1 1/2SM` is 1.5 statute miles, which is 2414 m, not the 3219 m that comes from reading the group as 2 statute miles.

`9999` and `10SM` both mean 10 km or more. METAR and TAF emit prevailing visibility `10000` metres with operator `ABOVE`.
