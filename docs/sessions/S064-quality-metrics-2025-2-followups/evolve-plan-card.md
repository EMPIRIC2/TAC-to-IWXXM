# Evolve Plan Card

> Cycle: EV-055 | Session: S064-quality-metrics-2025-2-followups | Updated: 2026-08-11  
> **Status: CLOSED** (`D-S064-close=1`)

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
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13` — **all completed**
- Skip: `03`, `06`

## Next child stage

**None** — cycle closed on stage (`D-S064-13=1`). Promote only if asked later.

## Risks / open decisions

- Promote `stage`→`main` deferred (explicit AskQuestion later)
- Live UJ-056 Playwright optional deferred (local T0 PASS)
