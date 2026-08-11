# Evolve Plan Card

> Cycle: EV-055 | Session: S064-quality-metrics-2025-2-followups | Updated: 2026-08-11

## Goal

Whitespace-normalize Quality metrics XML diffs (#982) and disposition/fix 2025-2
`SCHEMATRON_SKIPPED` (#980) and `SCHEMA_IMPORT_WARNING` (#979), preferring native
Schematron enable for xslt2 when feasible.

## Features

- F7.q — Quality metrics deepen (normalize + validate UX) — [Corpus: product §F7]
- F2 / F13 — iwxxm-validate Schematron/XSD for 2025-2 — [Corpus: product §F2] [Corpus: product §F13]
- F4 — only if version-line messaging needs it — [Corpus: product §F4]

## In / out of scope

- In: #982 normalize both sides + match_status; #980 investigate→prefer enable; #979 investigate→fix optional; operator Quality metrics surface; PR → stage
- Out: vendor hand-edits; redo #836 tab; DOKS EV-043/044; encode parity; stage→main unless asked

## Preset + routing

- Preset: **Standard**
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`
- Skip: `03`, `06`

## Next child stage

**02-verify-plan** — Gate A on AC1–AC7 + TC-EV055 + UJ-056 deepen + api-contract match_status

## Risks / open decisions

- Native Schematron may not fully support xslt2 → fall back to UX/document + child ticket
- XSD import fix may be catalog/packaging vs upstream pin gap
- Board WIP 3 > policy ≤2 (explicit override)
- Regenerating `corpus_metrics` blob after normalize may churn large fixtures
