# Evolve Plan Card

> Cycle: EV-055 | Session: S064-quality-metrics-2025-2-followups | Updated: 2026-08-11

## Goal

C14N-normalize Quality metrics XML diffs (#982) and **hard-fix** 2025-2
`SCHEMATRON_SKIPPED` (#980) and `SCHEMA_IMPORT_WARNING` (#979); panes default to
normalized XML with override to raw.

## Features

- F7.q — Quality metrics deepen (C14N diffs + pane override + validate UX) — [Corpus: product §F7]
- F2 / F13 — iwxxm-validate Schematron enable + XSD import fix for 2025-2 — [Corpus: product §F2] [Corpus: product §F13]

## In / out of scope

- In: #982 C14N both sides + match_status; #980 Schematron **enable required**; #979 import **fix required**; Quality metrics UI; PR → stage
- Out: vendor hand-edits; redo #836 tab; DOKS EV-043/044; encode parity; stage→main unless asked

## Preset + routing

- Preset: **Standard**
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`
- Skip: `03`, `06`

## Next child stage

**04-tech-plan** — execution plan + Build Plan Card (Gate A PASS `D-S064-gateA=1`)

## Risks / open decisions

- Native Schematron xslt2 support may be hard — cycle blocks/re-scopes if enable impossible (`D-S064-sch-hard=1`)
- XSD import fix may need catalog/packaging changes (`D-S064-xsd-hard=1`)
- Board WIP 3 > policy ≤2 (explicit override)
- C14N regen may churn large `corpus_metrics` fixtures
