# Context — bulletin year for issue and validity times

**Session:** `EV-1398-bulletin-year`
**Date:** 2026-10-14
**Mode:** standard evolve
**Ticket:** [#1398](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1398)
**Corpus:** [Corpus: product §F6] [Corpus: api] [Corpus: tests]

## Goal

IWXXM issue and validity times use the bulletin year and month. An impossible civil day fails with a clear message.

## Out of scope

- IWXXM version pin
- TAF `T24:00:00Z` unless a later test shows it is invalid
- Operator UI
- Other epic children

## Locked decision

Impossible days fail closed. Do not move day 31 in a 30-day month into the previous month.

## Inventory

| Piece | State on `stage` at `e4258697` |
|-------|--------------------------------|
| `fit_year_month` | Walks backward until the day exists. Day 31 in June becomes May |
| `iso_stamp` | Uses that fitted month and still writes the original day |
| Library `convert` without `bulletin_date` | Keeps example pins `2023-06` and `2012-08` |
| HTTP convert | Passes `bulletin_date` from the operator reference time, or the current UTC date when that field is blank |
| Abbreviated heading | Carries day and hour (`081200`), not a year |

## Checks still open

- A 2026-10-08 1200Z METAR issue time is October 2026 when the bulletin date is that month
- A SIGMET valid period uses that message year, not 2012
- Day 31 in a 30-day month fails closed with a clear message
