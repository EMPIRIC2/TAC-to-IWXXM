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

**Implement FE** (Lean) — `collapseEqualContext` + `/quality/:stem`; then **10-e2e**

## Locked intake (Phase 0)

| ID | Decision |
|----|----------|
| D-S066-route-shape | **1** — `/quality/:stem` + back-to-list |
| D-S066-context-n | **1** — 3 context lines |
| D-S066-list | **1** — navigate to detail; list via back |
| D-S066-01-ac | **1** — AC1–AC5 approved |
| D-S066-gateA | **1** — Gate A PASS |

## Risks / open decisions

- Staging CD for #987 may still be landing — evolve bases on merged stage tip `340b3cf6`
