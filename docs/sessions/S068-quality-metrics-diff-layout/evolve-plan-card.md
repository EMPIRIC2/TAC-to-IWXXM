# Evolve Plan Card

> Cycle: EV-058 | Session: S068-quality-metrics-diff-layout | Updated: 2026-08-17

## Goal

Selectable **inline (unified)** vs **side-by-side** XML diff on F7.q `/quality/:stem`, with preference persistence and synced-scroll polish; ship to stage; promote held.

## Features

- F7.q — side-by-side vs inline XML diff layout — [Corpus: product §F7.q]
- UJ-056 deepen — both layout modes — [Corpus: journeys §UJ-056] [Corpus: tests §UJ-056]

## In / out of scope

- In: layout toggle without reload; default unified; reuse `unifiedLineDiff`; localStorage/sessionStorage preference; optional synced scroll; Vitest + Playwright; PR → stage
- Out: API/backend; new npm `diff`; C14N/`match_status` semantics; #982 whitespace; promote to main; non–Quality-metrics UI

## Phase split

- Active phase: **Build**
- Spec→Build gate: **open** (`D-S068-spec-build=1a`)
- Preset: **Lean** (`D-S068-route=1a`)
- Gate A: **PASS** (`D-S068-gateA=1`)

## Spec-development band (00–06)

- Stages (ordered): `00 → 16 → 01 → 02`
- Dual-mode Spec skills: none
- Skip: `03`, `04`, `05`, `06`

## Build band (07–13) — blocked until gate

- Stages (ordered): `10 → 13`
- Dual-mode Build skills: none
- Deploy intent: **staging** (promote held)
- Skip: `07`, `08`, `09`, `11`, `12` (Lean — 16 Agent implements after Gate A)

## Next child stage

**CLOSED** — `D-S068-13=1` / `D-S068-close=1`; #994 → stage @ `2c320c45`; #983 Done; promote held

## Locked intake

| ID | Decision |
|----|----------|
| D-S068-ev-confirm | **1a** — EV0–EV9 carry-forward from E0–E8 |
| D-S068-route | **1a/2a/3a** — Lean bands; Spec→Build closed |
| D-S068-ui-preview | **1** — http://127.0.0.1:18000/ |
| D-S068-board | **1** — #983 In progress |
| D-S068-01-ac | **2b** — AC1–AC5; synced scroll best-effort |
| D-S068-01-control | **3a** — segmented Inline \| Side-by-side |
| D-S068-01-uj | **4a** — deepen UJ-056 + TC-EV058-* |

## Risks / open decisions

- Synced-scroll “if feasible” — confirm in 01 whether required or best-effort
- UJ-056: extend assertions vs new UJ id — prefer deepen UJ-056 (`D-S068-e1e2`)
