# 04-tech-plan — S040 / EV-032 (draft)

**Started**: 2026-08-04  
**Mode**: evolve delta  
**Features**: **F32** + deepen F23 (#835) / F4 / F6 / F2 / F13 (#808 + corpus)  
**Branch**: `evolve/EV-032-iwxxm-corpus-quality`  
**Status**: **in_progress** — Batch 1 locked; awaiting Batch 2 (`D-S040-04-batch-2`)

## Prior locks (from Gate A)

| Lock | Value |
|------|-------|
| VONA AHL / T1T2 | Defer to this stage (“when known”) — S02.M1 |
| Examples unlock | Incremental when F32 golden greens — S02.M2 |
| #808 depth | Docs + child issues only; #847 non-technical review — S02.M3 |
| Work order | #835 → #741 → #808 → corpus |
| Operator UI | Full F7 VONA (picker + Examples when unlocked) — E32-M2 |

## Interview locks — Batch 1 (`D-S040-04-batch-1` = 1,1,1,1)

| ID | Decision |
|----|----------|
| E32-T1 | Milestone structure **1** — M0–M4 (inventory → #835 → F32 → #808+#847 → corpus/closeout) |
| E32-T2 | #835 bar **1** — strict ADR-032 `canonicalize_xml` equality required for `wmoPass` |
| E32-T3 | F32 encode **1** — cookbook + fixtures first; plugin patterned on VAA/SWXA peers; guidance gaps → children |
| E32-T4 | VONA AHL **1** — discover in M2 from vendor/`vona-A7-1` + PANS-MET; no provisional T1T2 lock |

## Milestone shape (approved)

| M | Focus | Issues |
|---|--------|--------|
| M0 | Inventory / fixtures / gap index under #846 | corpus |
| M1 | #835 A6-2-TC ADR-032 equality → `wmoPass` + catalog | #835 |
| M2 | #741 / F32 VONA lint → convert → validate (+ FE) | #741 |
| M3 | #808 + #847 adoptability docs / checklists | #808, #847 |
| M4 | Corpus children + verify/deploy closeout | #846 |

## Interview Batch 2 — see chat (`D-S040-04-batch-2`)
