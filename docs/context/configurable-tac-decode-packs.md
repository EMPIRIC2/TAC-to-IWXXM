# Context — configurable TAC decode packs

**Session:** `EV-configurable-tac-decode-packs`
**Date:** 2026-09-19
**Mode:** scoped evolve (full)
**Corpus:** [Corpus: product §F6] [Corpus: product §F9] [Corpus: product §F23] [Corpus: product §F28] [Corpus: product §F32] [Corpus: system-spec] [Corpus: api] [Corpus: adr/ADR-032] [Corpus: adr/ADR-044]

## Goal

Replace hardcoded TAC explainers with a configurable pack engine that produces natural-language decode and, in the same cycle, the convert intermediate representation. Vendor XML goldens stay byte-identical.

## Locked intake

| Topic | Lock |
|---|---|
| Pairing | Convert parsers move onto the same packs this cycle |
| SIGMET | Three packs (ordinary, VA, TC). HTTP stays `product=sigmet` |
| Products | METAR/SPECI, TAF, AIRMET, VAA, TCA, SWXA, VONA are core. WAFS/QVACI are stubs |
| Layouts | Whitespace-token vs label-field. Commas and hyphens are value delimiters, not a VONA file type |
| Bulletins | TAC abbreviated-heading multi-report text, plus COLLECT |
| COLLECT | If TAC is inside, decode those reports. If only XML, walk fields. No encoder in `tac-decoding` |
| Goldens | Existing `vendor/schemas` plus in-repo fixtures. Do not copy new WMO files |
| XML | Byte-identical |
| i18n | Locale hook, English templates only |
| UI | No local preview this pass. No in-app pack editor |
| Research note | Not path authority. VONA is IWXXM in this repo (F32, `vona.xsd`) |

## Problem / users

Operators and library users get uneven explanations: METAR groups that contain spaces become residuals, while VAA/SWXA/VONA are special-cased in Python. Convert parses the same text again in `products/*.py`, so the two paths drift. The pain shows up on `/decode-tac` and whenever a residual is copied into remarks.

## Must not break

- Vendor peer XML equality for convert
- `POST /api/v1/decode-tac` response fields already shipped
- `product=sigmet` selecting `iwxxm:SIGMET` / `VolcanicAshSIGMET` / `TropicalCycloneSIGMET` from TAC
- F28 SWXA and F32 VONA quality bars
- `tac-decoding` stays free of FastAPI, Supabase, and IWXXM encode

## Inventory

| Area | Today |
|---|---|
| Decode | `packages/tac-decoding` (`decode.py`, glossary YAML, catalog) |
| Shims | `packages/tac2iwxxm/decode.py`, `glossary.py` |
| Convert IR | `packages/tac2iwxxm/products/*.py` (`swxa.py`, `vona.py`, SIGMET, …) |
| Bulletin split | `tac2iwxxm.bulletin.split_bulletin` — decode still imports this |
| HTTP | `apps/backend/src/routers/tac_quality.py` `POST /decode-tac` |
| Examples | `vendor/schemas/iwxxm/**/examples/` including `vona-A7-1`, `spacewx-A7-*`, SIGMET VA/TC, COLLECT samples |

## Build intent (gate closed)

Engine and packs in `tac-decoding`. `tac2iwxxm` depends on that package for IR and must not be imported by decode. Backend changes only if optional segment fields ship. Issue ticket is created during requirements.

## Memory

Session-open retrieve matched nothing accepted for this query. Historical retrieve returned one unrelated vecinita question; waived.

## Next

`spec-development/requirements` (delta). Feature id, acceptance tests, and the COLLECT XML-walk contract are still open there.
