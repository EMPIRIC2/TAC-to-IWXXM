# Evolve Plan Card

> Cycle: EV-057 | Session: S067-m0-ready-apex-accumulate-validate | Updated: 2026-08-15

## Goal

Ship M0 Ready **#948**, **#903**, and **#838** to `stage` (Standard); promote only after separate re-approve.

## Features

- F7 (operator UI deepen) — #903 / #838 — [Corpus: product §F7]
- F1 / F6 (convert + archive path) — #903 — [Corpus: product §F1] [Corpus: product §F6]
- F2 / F4 (validate + version) — #838 — [Corpus: product §F2] [Corpus: product §F4]
- Deploy / hosts — #948 apex redirect — [Corpus: tech-spec] [Corpus: deploy]

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

**01-requirements** (delta) — lock AC / journeys / corpus deltas for #948, #903, #838 before Gate A.

## Risks / open decisions

- #948: DNS / ingress / cert ownership — surface early in 01/04 if access unclear
- #903: stem length / ICAO vs TAC prefix; accumulate caps — interview in 01
- #838: which validate endpoint(s) for raw IWXXM; multi-file/zip stretch vs v1 paste+single upload
- Promote held until all three on stage (`D-S067-promote=2b`)
- WIP: only #948 In progress until later milestones start #903/#838

## Locked intake (Phase 0)

| ID | Decision |
|----|----------|
| D-S067-first | **1a** — #948 first |
| D-S067-pack | **2c** — one cycle all three Ready |
| D-S067-success | **3c** — stage + promote path |
| D-S067-oos | **1a** — defaults |
| D-S067-promote | **2b** — stage all three; promote after re-approve |
| D-S067-blockers | **3a** — none known |
| D-S067-preset | **4a** — Standard |
| D-S067-order | **2a** — #948 → #903 → #838 |
| D-S067-ui-preview | **3a** — remind at 11 |
| D-S067-proceed | **4a** — open session |
| D-S067-board | **1** — #948 In progress |
