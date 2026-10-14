# Context — forecast variable wind in knots

**Session:** `EV-1400-taf-vrb-knots`
**Date:** 2026-10-14
**Mode:** micro evolve
**Ticket:** [#1400](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1400)
**Corpus:** [Corpus: product §F6] [Corpus: tests]

## Goal

A TAF `VRB` group keeps its speed and gust in the TAC unit, and keeps the variable-direction flag.

## Out of scope

- METAR variable wind
- Unit conversion for a numbered wind direction
- Operator UI
- Other epic children

## Locked decision

The forecast parser already stores the speed and gust. The TAF wind writer was discarding them and emitting `0.0` m/s whenever the direction was variable. The writer now uses the stored speed, gust, and TAC unit, and still sets `variableWindDirection` true.

## Checks

- `VRB03KT` is 3 knots
- `VRB10G20KT` keeps a 10-knot mean and a 20-knot gust
- Both omit a mean wind direction
