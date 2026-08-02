# 04-tech-plan — S036 / EV-029

**Started**: 2026-08-01  
**Mode**: evolve delta  
**Features**: **F28** + deepen F6 / F12 / F2 / F13 / F15 / F20 / F23 / F24 / F26 / F27  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Status**: **in_progress** — Batch 1 locked; Batch 2 pending

## Toolchain baseline (detected)

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| Packages | `tac2iwxxm`, `tac-validate`, `iwxxm-validate`; FE Vite |
| Registry | ADR-028 reuse (add SWXA + family rows) |
| Golden compare | ADR-032 `canonicalize_xml` (+ `wmoReference` OK for SWXA v1 — S02.L1) |
| Runtime SoT | Vendor IWXXM **2025-2** |
| API | Additive `product=swxa` (docs lead; enum in 07 — S02.M1) |
| Deploy | Existing Render API (+ FE only if Examples unlock) |
| New deps | Pending Batch 2 |

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
| E29-T4 | CI **2** — **separate workflow per family** (pattern: `sigmet-quality.yml` / `wmo-quality.yml`) |

## Draft milestone order (Batch 1 → refine in Batch 2)

| M | Focus | Gate |
|---|--------|------|
| **M0** | Full eight-family re-mine + promote + example inventory + coverage matrix | **No Phase B until M0 complete** |
| M1 | AHL / COM / shared `T1T2` + filename/`bulletinIdentifier` (`tac2iwxxm`) | after M0 |
| M2 | METAR | after M1 |
| M3 | SPECI | after M2 |
| M4 | TAF | after M3 |
| M5–M7 | SIGMET gen / VA / TC (+ CNL) — **split vs single pending Batch 2** | after M4 |
| M8 | AIRMET | |
| M9 | VAA (#820 / #823 B4) | |
| M10 | TCA | |
| M11 | SWXA (**F28**) + `product=swxa` runtime | |
| M12 | Smoke / 08 / 09 / 10 / 11 / 12 / 13 | |

## CI sketch (Batch 1)

Separate workflows (names TBD in execution plan), e.g.:

- `ahl-com-quality.yml` (or fold AHL into first product pack)
- `metar-quality.yml` / `speci-quality.yml` / `taf-quality.yml` (or extend existing aerodrome packs)
- `sigmet-quality.yml` (extend) + TC/VA packs as needed
- `airmet-quality.yml`, `vaa-quality.yml`, `tca-quality.yml`, `swxa-quality.yml`
- Keep root `ci.yml` matrix

## Artifacts

- `reports/execution-plan.md` — pending Batch 2 + approve
- This report — Batch 1 locked

## Next

**Batch 2** — deps / deploy / SIGMET split / kill-switch → draft execution-plan → approve → Gate B → 07.
