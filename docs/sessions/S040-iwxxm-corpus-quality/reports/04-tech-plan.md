# 04-tech-plan — S040 / EV-032 (draft)

**Started**: 2026-08-04  
**Mode**: evolve delta  
**Features**: **F32** + deepen F23 (#835) / F4 / F6 / F2 / F13 (#808 + corpus)  
**Branch**: `evolve/EV-032-iwxxm-corpus-quality`  
**Status**: **in_progress** — awaiting Batch 1 (`D-S040-04-batch-1`)

## Prior locks (from Gate A)

| Lock | Value |
|------|-------|
| VONA AHL / T1T2 | Defer to this stage (“when known”) — S02.M1 |
| Examples unlock | Incremental when F32 golden greens — S02.M2 |
| #808 depth | Docs + child issues only; #847 non-technical review — S02.M3 |
| Work order | #835 → #741 → #808 → corpus |
| Operator UI | Full F7 VONA (picker + Examples when unlocked) — E32-M2 |

## Proposed milestone shape (pending approval)

| M | Focus | Issues |
|---|--------|--------|
| M0 | Inventory / fixtures / gap index under #846 | corpus |
| M1 | #835 A6-2-TC ADR-032 equality → `wmoPass` + catalog | #835 |
| M2 | #741 / F32 VONA lint → convert → validate (+ FE) | #741 |
| M3 | #808 + #847 adoptability docs / checklists | #808, #847 |
| M4 | Corpus children + verify/deploy closeout | #846 |

## Interview Batch 1 — see chat (`D-S040-04-batch-1`)
