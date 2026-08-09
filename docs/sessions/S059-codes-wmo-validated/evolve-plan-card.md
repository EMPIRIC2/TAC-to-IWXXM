# Evolve Plan Card

> Cycle: EV-050 | Session: S059-codes-wmo-validated | Updated: 2026-08-09

## Goal

Ship **Validated** for `#889`: offline harvest from `vendor/schemas/iwxxm-codelists`
(+ vendored RDF) and wire `tac-validate` / matrix tests so agreed TAC tokens are
membership-checked in CI — no live `codes.wmo.int` HTML in PR CI.

## Features

- Deepen **F12**, **F15**, **F20**, **F23**, **F24**, **F28** (no new Fn) —
  [Corpus: product]
- Parent [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) Validated —
  child [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) — [Corpus: tests]
- SoT / pin cadence — [Corpus: tech-spec]

## In / out of scope

- In: offline harvest; membership happy/sad for weather/recent/cloud/SIGMET+AIRMET
  phenomena/nilReason; aggressive fixtures (RE*, AIRMET `_`, SpaceWx, TCU); cadence docs;
  #882 design-only compose note
- Out: vendor hand-edits; live HTML PR CI; `iwxxm-validate` replace; full #882 job;
  `#958`; `stage`→`main`; exhaustive 402 wx combos

## Preset + routing

- Preset: **Standard** (`D-S059-route=1`)
- Stages: `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`
- Skip: `03`, `06`, `10`, `12`, `13`
- Intake: `D-S059-families=1a`, `D-S059-fixtures=2c`, `D-S059-882=3a`, `D-S059-01-ac=4a`

## Next child stage

**02-verify-plan** — Gate A (after user approves 01 preview + commit)

## Risks / open decisions

- Aggressive fixtures enlarge 07 scope (F24/F28 packs) — watch milestone sizing in 04
- Docs PR [#964](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/964) → `stage` still open
- 01 deltas drafted locally — **preview held; no push yet**
