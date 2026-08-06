# Evolve Plan Card

> Cycle: EV-040 | Session: S048-workbench-lint-ux | Updated: 2026-08-06

## Goal

Clearer workbench lint/UX, slim prefs, official AHL/Collect examples, catalog source attribution, and corrected example lint FPs.

## Features

- F7 — Multi-product TAC operator UI — [Corpus: product §F7]
- F10 — Workbench preview / lint UX — [Corpus: product §F10]
- F15 — Lint issue registry + catalog — [Corpus: product §F15] [Corpus: adr/ADR-028]

## In / out of scope

- In: console lines; input preserve; New TAC + button strip; prefs name/ext; official AHL/Collect; catalog source; RVR/AHL FP fixes
- Out: F16–F19; F8; F22 rewrite; new Fn

## Preset + routing

- Preset: Standard
- Stages: 00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13

## Next child stage

01-requirements — delta ACs from locked plan

## Risks / open decisions

- Prefs localStorage migration for removed keys
- Catalog API additive fields must ship with FE
