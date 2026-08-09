# Evolve Plan Card

> Cycle: EV-048 | Session: S057-strip-internal-doc-refs | Updated: 2026-08-08

## Goal

Strip internal engineering document references from operator UI copy and public
API/OpenAPI surfaces, with an automated regression guard. [#951]

## Features

- F7 — Multi-product operator UI (deepen copy hygiene) — [Corpus: product §F7]
- F21 — Public unauthenticated operator app (deepen OpenAPI/error copy) — [Corpus: product §F21]
- [Corpus: api] · [Corpus: tests]

## In / out of scope

- In: UI strings; OpenAPI descriptions; client-facing errors; automated guard; unit/OpenAPI tests
- Out: source comments; test names/docstrings; docs/ADRs/sessions; commit/PR citation rules

## Preset + routing

- Preset: **Standard** (`D-S057-preset-reconfirm=1`)
- Stages: `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11`
- Skip: `03`, `06`, `12`, `13`

## Next child stage

**08-verify-build** — M1–M3 implementation done; tip CI / local verify

## Risks / open decisions

- UI preview: http://localhost:5173/
- OpenAPI stripped; BE+FE guards green; T3.3 Playwright skipped (no FE hits)
- `#NNN` pattern uses `(?<!\w)#\d{3,}\b` (lookbehind; `\b#` missed `#702`)
