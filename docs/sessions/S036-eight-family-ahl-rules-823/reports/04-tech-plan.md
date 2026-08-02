# 04-tech-plan — S036 / EV-029

**Started**: 2026-08-01  
**Mode**: evolve delta  
**Features**: **F28** + deepen F6 / F12 / F2 / F13 / F15 / F20 / F23 / F24 / F26 / F27  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Status**: **in_progress** — Batches 1–2 locked; plan approve pending

## Toolchain baseline (detected)

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| Packages | `tac2iwxxm`, `tac-validate`, `iwxxm-validate`; FE Vite |
| Registry | ADR-028 reuse (add SWXA + family rows) |
| Golden compare | ADR-032 `canonicalize_xml` (+ `wmoReference` OK for SWXA v1 — S02.L1) |
| Runtime SoT | Vendor IWXXM **2025-2** |
| API | Additive `product=swxa` (docs lead; enum in 07 — S02.M1) |
| Deploy | API redeploy; H1–H3; H4–H5 waive unless FE (E29-T6=1) |
| New deps | Prefer none; AskQuestion per new dep (E29-T5=1) |

## Pre-locked from 02

| ID | Lock |
|----|------|
| S02.M1 | Runtime `swxa` enum in **07-build** |
| S02.M2 | TC SIGMET = **F23 deepen** (not new Fn) |
| S02.M3 | Phase A may leave child issues; #823 stays open |
| S02.L1 | SWXA golden may be `wmoReference` in v1 |

## Interview locks — Batch 1 (`D-S036-04-batch-1` = 3,1,2,2)

| ID | Decision |
|----|----------|
| E29-T1 | Milestone structure **3** — one milestone per product (METAR / SPECI / TAF separate) |
| E29-T2 | AHL home **1** — extend `packages/tac2iwxxm` bulletin/AHL; dissemination imports; ADR only if needed |
| E29-T3 | Mining **2** — **full re-mine all eight families before any Phase B code** |
| E29-T4 | CI **2** — **separate workflow per family** |

## Interview locks — Batch 2 (`D-S036-04-batch-2` = 1,1,1,1)

| ID | Decision |
|----|----------|
| E29-T5 | Deps **1** — none expected; AskQuestion before adding any |
| E29-T6 | Deploy **1** — API redeploy; H1–H3; H4–H5 waive unless FE Examples unlock |
| E29-T7 | SIGMET Ms **1** — three milestones: gen / VA / TC |
| E29-T8 | Kill-switch **1** — HARD themes; block → AskQuestion |

## Approved milestone order (pending plan Approve)

| M | Focus |
|---|--------|
| **M0** | Full eight-family re-mine + promote + inventory + matrix (**no Phase B until done**) |
| M1 | AHL / COM / shared `T1T2` + filename (`tac2iwxxm`) |
| M2 | METAR |
| M3 | SPECI |
| M4 | TAF |
| M5 | General SIGMET |
| M6 | VA SIGMET |
| M7 | TC SIGMET (#738) |
| M8 | AIRMET |
| M9 | VAA (#820) |
| M10 | TCA |
| M11 | SWXA (**F28**) + `product=swxa` runtime |
| M12 | Smoke / 08–13 |

## Artifacts

- `reports/execution-plan.md` — **draft** (48 tasks) — approve pending
- This report — Batches 1–2 locked

## Next

Plan approve AskQuestion → Gate B → complete 04 → **07-build @ T0.1**.
