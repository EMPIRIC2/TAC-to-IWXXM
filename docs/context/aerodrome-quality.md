# Context — Aerodrome quality (TAF + SPECI) (S020 / EV-015)

Scoped brief for F15 sequel. Full discovery lives in 01-requirements + domain matrix.

## Tickets

| Issue | Product | IWXXM root | Stance this cycle |
|-------|---------|------------|-------------------|
| [#735](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/735) | TAF | `iwxxm:TAF` | Full quality bar |
| [#734](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/734) | SPECI | `iwxxm:SPECI` | Full quality bar (parallel) |

## Stack (mirror EV-011)

- `packages/tac-validate` — registry codes (ADR-028), accept/negative
- `packages/tac2iwxxm` — goldens / product_matrix / annex3 + iwxxm_us
- `packages/iwxxm-validate` — XSD + Schematron round-trip
- `docs/domain/rules/COVERAGE_MATRIX.md` — TAF + SPECI rows
- WMO encode: `vendor/schemas/iwxxm/2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt` + 2025-2 corrections (no `runwayState`)

## Predecessor (F15)

METAR/SPECI R1–R8 closed in EV-011 (#742). SPECI already has shared `metarSpeci` pack + adjacency tests; this cycle still executes **#734 full AC** (fixtures, roots, guidance audit, mis-classification) alongside TAF deepen.

## Out of scope (siblings)

#731 AIRMET, #733/#738/#739 SIGMET family, #736 VAA, #737 TCA, #740 SWX, #741 VONA — unless shared common-rule work requires a linked stub.
