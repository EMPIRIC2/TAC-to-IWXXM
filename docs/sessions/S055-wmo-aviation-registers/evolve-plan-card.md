# Evolve Plan Card

> Cycle: EV-046 | Session: S055-wmo-aviation-registers | Updated: 2026-08-08

## Goal

Present → cite → cover aviation `codes.wmo.int` registers for all F6 product families
(Lean docs/coverage); waive Validated with Standard follow-on.

## Features

- F6 / F12 / F15 / F20 / F23 / F24 / F26 / F27 / F28 / F32 deepen — [Corpus: product]
- Tests TC-EV046-001..006 — [Corpus: tests]

## In / out of scope

- In: inventory, citations (incl. ISSUE_CATALOG), coverage %, gap backlog, Validated waiver
- Out: harvest CI wiring; live HTML PR CI; #882 notify; vendor hand-edits

## Preset + routing

- Preset: **Lean** (`D-S055-open=2`)
- Stages: `00 → 16 → 01 → 02`
- Skip: `03`–`13`

## Next child stage

**02-verify-plan** — Gate A pending (`D-S055-gateA`)

## Risks / open decisions

- GraphQL rate limit blocked Project #7 Status sync — retry
- Full F6 sweep is large for Lean — coverage % may be coarse with many exclusions (M1)
- Standard follow-on must be filed before Lean close (AC5)
- After Gate A PASS: execute Lean docs on branch (no 04/07), then close cycle
