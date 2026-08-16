# Evolve Plan Card

> Cycle: EV-057 | Session: S067-m0-ready-apex-accumulate-validate | Updated: 2026-08-16

## Goal

Ship M0 Ready **#948**, **#903**, and **#838** to `stage` (Standard); promote only after separate re-approve.

## Features

- F7.r — Accumulate conversions → one ZIP (#903) — [Corpus: product §F7]
- F7.s — Validate existing IWXXM paste/upload (#838) — [Corpus: product §F7]
- F30 deepen — Apex → app redirect (#948) — [Corpus: product §F30] [Corpus: deploy]
- F1/F6 notes (#903); F2/F4 notes (#838) — [Corpus: product §F1] [Corpus: product §F6]
  [Corpus: product §F2] [Corpus: product §F4]
- Journeys: UJ-057 / UJ-058 / UJ-OPS-002 — [Corpus: journeys] [Corpus: tests]

## Phase split

- Active phase: **Build complete** (awaiting Phase 4 close)
- Spec→Build gate: **open** (historical)
- 13: **COMPLETE** (`D-S067-13=1a`)
- Promote: **held** (`D-S067-promote=2b`)

## Next

Phase 4 close AskQuestion — close cycle / 15-service-health / promote / 17-retrospective.

## PRs

- #991 → `stage` @ `d7022f1f`
- #992 → `stage` @ `3af364fb` (UJ-058 aria-label)
