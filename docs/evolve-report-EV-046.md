# Evolve report — EV-046

> S055-wmo-aviation-registers · 2026-08-08 · Lean · #889

## Summary

Operationalized present → cite → cover for aviation `codes.wmo.int` registers against
offline `iwxxm-codelists` / pin RDF. Validated automated membership deferred to #959.

## Features deepened

F6 / F12 / F15 / F20 / F23 / F24 / F26 / F27 / F28 / F32 (no new Fn).

## Artifacts

- `docs/sessions/S055-wmo-aviation-registers/reports/codes-wmo-int-coverage.md`
- `docs/domain/rules/PROVENANCE_MAP.json` + regenerated ISSUE_CATALOG*
- `docs/domain/rules/COVERAGE_MATRIX.md` · `RULE_SOURCE_URLS.md`
- `docs/domain/mining/codes-wmo-int-aviation-mining-notes.md`
- `scripts/tac-validate/regen_issue_catalog.py` (URL-first attribution)

## Gates

| Gate | Result |
|------|--------|
| A (02) | PASS (`D-S055-gateA=1`) |
| B–D | N/A (Lean skip 04–13) |

## Follow-ons

- [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) — Validated / harvest CI
- [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) — URI drift
- [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) — notify pipeline
