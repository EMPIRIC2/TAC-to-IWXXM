# Failed-translation minimum identity fields

Session: EV-1292-failed-shell-fields. Ticket: #1292. Scale: standard. Gate: open.

[Corpus: product §F6] [Corpus: tests] [Corpus: domain-mining]

## Goal

Each failed-translation shell carries the minimum identity fields the 5th-edition OPMET exchange guidelines list for that product, and still carries the original TAC.

The element names are the 2025-2 Schematron failed-translation asserts. Those asserts are the machine form of guidelines §5.3.3. Weather parameters stay off the shell.

## Out of scope

Do not reopen test and exercise usage (#1276). Do not send the message over AMHS. Do not add phenomenon, analysis, observation, or forecast bodies. Do not promote `stage` to `main`.

## Comparison

| Product | Minimum identity fields | On the failed shell now |
|---|---|---|
| METAR | issue time, aerodrome, observation time | Present |
| SPECI | issue time, aerodrome, observation time | Present |
| TAF | issue time, aerodrome, valid period | Valid period missing |
| SIGMET | issue time, issuing ATS unit, valid period | Issuing unit and valid period missing |
| AIRMET | issue time, issuing ATS unit, valid period | Issuing unit and valid period missing |
| VAA | issue time, issuing volcanic ash advisory centre | Issuing centre missing |
| TCA | issue time, issuing tropical cyclone advisory centre | Issuing centre missing |
| SWXA | issue time, issuing space weather centre | Issuing centre missing |

`translationFailedTAC` and operational `permissibleUsage` are already present on every shell.

## Locked rule

- Add only the missing identity fields in the table.
- Recover a designator from the TAC when the TAC has one. When it does not, write the element with a missing nil reason. Do not invent `YUZZ` or a fictional centre name.
- Leave `translationFailedTAC` as the original TAC and `permissibleUsage` as operational.

## Success

- The table above is the present/missing record.
- Each missing identity field is added on that product's failed shell.
- `translationFailedTAC` remains the original TAC, and `permissibleUsage` stays operational.
