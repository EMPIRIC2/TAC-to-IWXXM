# Evolve Plan Card

> Cycle: EV-056 | Session: S066-quality-metrics-diff-page | Updated: 2026-08-11

## Goal

Dedicated Quality metrics detail route with GitHub-style collapsible unified XML diffs; C14N equality unchanged.

## Features

- F7.q — Quality metrics detail page + collapsible diffs — [Corpus: product §F7.q]
- UJ-056 deepen — [Corpus: journeys §UJ-056] [Corpus: tests §UJ-056]

## In / out of scope

- In: `/quality/:stem` (or shell-equivalent) shareable detail; pretty C14N panes; hunk fold/expand; FE unit + UJ-056 e2e; PR → stage
- Out: `match_status` / C14N semantics; new npm diff lib unless AskQuestion; promote to main; API contract unless routing requires

## Preset + routing

- Preset: **Lean** (`D-S066-route=1`)
- Stages (ordered): `00 → 16 → 01 → 02 → 10 → 13`
- UI preview: non-deployed http://127.0.0.1:18000/ (`D-S066-ui-preview=1`)
- Issue: #988 In progress · base `stage@340b3cf6`

## Next child stage

**01-requirements** (delta) — lock AC1–AC5 from FOLLOWUP; deepen F7.q + UJ-056; no new Fn

## Risks / open decisions

- Route shape (React Router path vs shell tab query) — decide in 01
- Default collapsed context lines (suggest 3) — decide in 01
- Staging CD for #987 still landing — evolve bases on merged stage tip
