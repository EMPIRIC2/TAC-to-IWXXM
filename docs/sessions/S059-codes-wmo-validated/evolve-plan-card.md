# Evolve Plan Card

> Cycle: EV-050 | Session: S059-codes-wmo-validated | Updated: 2026-08-09

## Goal

Ship **Validated** for `#889`: offline harvest from `vendor/schemas/iwxxm-codelists`
(+ vendored RDF) and wire `tac-validate` / matrix tests so agreed TAC tokens are
membership-checked in CI — no live `codes.wmo.int` HTML in PR CI.

## Features

- Deepen **F6**, **F12**, **F15**, **F20**, **F23**, **F24**, **F28** (no new Fn) —
  [Corpus: product]
- Parent [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) Validated —
  child [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) — [Corpus: tests]
- SoT / pin cadence — [Corpus: tech-spec]
- Profiles: **`annex3` vs `iwxxm_us`** compare + true-error fixes — [Corpus: product §F6]

## In / out of scope

- In: offline harvest; membership happy/sad for weather/recent/cloud/SIGMET+AIRMET
  phenomena/nilReason; aggressive fixtures (RE*, AIRMET `_`, SpaceWx, TCU); cadence docs;
  #882 design-only compose note; **profile compare + fix true errors (AC7–AC8)**
- Out: vendor hand-edits; live HTML PR CI; `iwxxm-validate` replace; full #882 job;
  `#958`; `stage`→`main`; exhaustive 402 wx combos; country scorecards beyond two profiles

## Preset + routing

- Preset: **Standard** (`D-S059-route=1`)
- Stages: `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`
- Skip: `03`, `06`, `10`, `12`, `13`
- Intake: `D-S059-families=1a`, `D-S059-fixtures=2c`, `D-S059-882=3a`, `D-S059-01-ac=4a`
- Amend: `D-S059-profiles=1b` — all F6; `iwxxm_us` N/A where unsupported; AC7–AC8 locked

## Next child stage

**05-verify-tech** — Gate B (`D-S059-04-plan=1` approved)

## Risks / open decisions

- Aggressive fixtures + dual-profile matrix enlarges 07 — size milestones in 04
  (advisory M3: may split M1 harvest / M2 fixtures / M3 profiles)
- True-error volume unknown until compare runs — AC8 defer+cite OK (advisory M1)
- Full F6 matrix: many products are N/A for `iwxxm_us` — must not fail those rows (M2)
- Docs PR [#964](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/964) → `stage` still open

## Gate A

**PASS** `D-S059-gateA=1` (2026-08-09) — report `reports/02-verify-plan.md`
