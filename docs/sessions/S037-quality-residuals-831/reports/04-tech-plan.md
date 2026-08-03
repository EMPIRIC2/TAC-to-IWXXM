# 04-tech-plan — S037 / EV-030

**Started**: 2026-08-03  
**Mode**: evolve delta  
**Features**: **F29** + deepen F23 / F12 / F2 / F13 / F9 / F26 / F27  
**Branch**: `evolve/EV-030-quality-residuals-831`  
**Status**: **in_progress** — Batch 1 locked; Batch 2 interview

## Toolchain baseline (detected)

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| Packages | `tac-validate`, `tac2iwxxm`, `iwxxm-validate`; FE Vite (catalog only if #829 unlock) |
| Registry | ADR-028 reuse (TC SIGMET codes for #829) |
| Golden / catalog | ADR-032 tier for `sigmet-A6-2-TC` (#829) |
| Runtime SoT | Vendor IWXXM **2025-2** |
| API | No new product enum; lint catalog additive; decode deepen (#820) |
| New deps | Prefer none; AskQuestion per new dep (Batch 2) |
| Deploy | H1–H3 if API behavior ships; H4–H5 when FE catalog unlock ships (Batch 1 → unlock default) |

## Pre-locked from 02

| ID | Lock |
|----|------|
| S02.M1 | #831 pilot = **METAR/SPECI** lint+encode+validate first |
| S02.M2 | #829 STNR/geometry may be **OOS with cite** |
| S02.M3 | #820 may leave **child residual** |
| S02.L1 | #831 harness = **session design note** unless 04 needs ADR |

## Interview locks — Batch 1 (`D-S037-04-batch-1` = 1,1,1,1)

| ID | Decision |
|----|----------|
| E30-T1 | Milestone structure **1** — **M0–M4** as proposed |
| E30-T2 | #831 case storage **1** — **YAML/JSON under testdata** + pytest load |
| E30-T3 | Rule inventory SoT **1** — **unified index** (registry / Schematron assert / encode row → matrix slots) |
| E30-T4 | #829 catalog unlock **1** — unlock when quality path green (ADR-032 `wmoPass`/`wmoReference`) |

## Approved milestone order (pending Batch 2 + Gate B)

| M | Focus |
|---|--------|
| **M0** | #831 design note (eval Qs) + RuleCase / runner API spike + unified inventory sketch |
| **M1** | F29 runners + YAML case load + METAR/SPECI pilot + inventory gate + CI smoke |
| **M2** | #829 TC SIGMET lint pack + STNR/OOS + A6-2-TC catalog unlock |
| **M3** | #820 VAA/TCA decode deepen + matrix/allowlist |
| **M4** | Smoke / 08–13 (H4–H5 if FE unlock ships) |

## Next

Batch 2 AskQuestion → draft execution-plan → Gate B.
