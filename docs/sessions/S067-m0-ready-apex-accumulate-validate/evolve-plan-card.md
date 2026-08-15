# Evolve Plan Card

> Cycle: EV-057 | Session: S067-m0-ready-apex-accumulate-validate | Updated: 2026-08-15

## Goal

Ship M0 Ready **#948**, **#903**, and **#838** to `stage` (Standard); promote only after separate re-approve.

## Features

- F7.r — Accumulate conversions → one ZIP (#903) — [Corpus: product §F7]
- F7.s — Validate existing IWXXM paste/upload (#838) — [Corpus: product §F7]
- F30 deepen — Apex → app redirect (#948) — [Corpus: product §F30] [Corpus: deploy]
- F1/F6 notes (#903); F2/F4 notes (#838) — [Corpus: product §F1] [Corpus: product §F6]
  [Corpus: product §F2] [Corpus: product §F4]
- Journeys: UJ-057 / UJ-058 / UJ-OPS-002 — [Corpus: journeys] [Corpus: tests]

## In / out of scope

- In: #948 redirect + docs; #903 accumulate + ZIP naming + clear; #838 paste/upload validate-only; stage smoke; board hygiene
- Out: #841 / #727 / #874; S056 ruleset-admin leftover; batch disseminate; TAC reverse from IWXXM; auto-promote

## Preset + routing

- Preset: **Standard** (`D-S067-preset=4a`)
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 → 10 → 11 → 12 → 13`
- Skip: 03 / 05 / 06 unless AskQuestion
- UI preview: remind at 11-verify-impl (`D-S067-ui-preview=3a`)
- Issue order: **#948 → #903 → #838**
- Base: `stage@b796882e`

## Next child stage

**04-tech-plan** — execution plan / milestones (#948 → #903 → #838). Gate A PASS.

## Risks / open decisions

- #948: TLS/DNS for apex/www must exist or be provisioned with Ingress change
- #838: confirm validate multipart covers paste/upload in 04 (re-open api only on gap)
- Promote held until all three on stage (`D-S067-promote=2b`)
- WIP: only #948 In progress until later milestones start #903/#838

## Locked intake (Phase 0 + 01 + Gate A)

| ID | Decision |
|----|----------|
| D-S067-first | **1a** — #948 first |
| D-S067-pack | **2c** — one cycle all three Ready |
| D-S067-preset | **4a** — Standard |
| D-S067-order | **2a** — #948 → #903 → #838 |
| D-S067-01-ac | **1** — AC approved |
| D-S067-903-cap | **1c** — ≤200 |
| D-S067-948-ingress | **2a** — extend prod FE Ingress |
| D-S067-gateA | **1** — PASS → 04 |
