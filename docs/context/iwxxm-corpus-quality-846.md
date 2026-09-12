# Scoped context — Official IWXXM corpus quality (#846)

| Field | Value |
|-------|-------|
| Status | active |
| Session | S040-iwxxm-corpus-quality |
| Evolve | EV-032 |
| Created | 2026-08-04 |
| Features | **F32** (new); deepen F23 (#835), F4/F6/F2/F13 (#808 + corpus) |
| GitHub | [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) epic; children #835, #741, #808 |

## Resolutions

| ID | Decision |
|----|----------|
| R1 | Umbrella = **new Epic #846** (not expand #808; not #836) |
| R2 | One cycle = #835 + #741 + #808 + corpus/WMO-source track |
| R3 | VONA = **F32** quality bar (peer F23–F28) |
| R4 | Order = #835 → #741 → #808 → corpus children |
| R5 | Exclude metrics UI #836 / workbench epic #840 from this cycle |

## Problem

Product quality bars F15–F28 / F29 closed most Annex-3 family gaps, but:

1. **#835** — A6-2-TC still `wmoReference`; ADR-032 equality vs vendor XML not yet green
2. **#741** — VONA never encoded (OOS in S036); guidance file silent; XSD+SCH+`vona-A7-1` authority
3. **#808** — Next IWXXM line adoptability unassessed (support window latest+1)
4. **Corpus** — Need ongoing pass rates vs official examples and WMO sibling sources (translation, codelists, codes.wmo.int, modelling), not only one-off mining (#804/#807 closed)

## Authority sources

- Vendor pin SoT: `vendor/manifest.json` (today **2025-2**)
- https://github.com/wmo-im/iwxxm
- https://github.com/wmo-im/iwxxm-translation
- https://github.com/wmo-im/iwxxm-codelists
- https://codes.wmo.int/
- https://github.com/wmo-im/iwxxm-modelling

## Non-goals

- #836 Quality metrics tab UI
- Re-pin / ship new IWXXM line inside #808
- Edit `vendor/schemas/*` outside sync PRs

## Next

Approve `D-S040-route` (Standard routing) → cut `evolve/EV-032-iwxxm-corpus-quality` from `main` → 16-evolve Phase 1 (Fn confirm + 01-requirements).

## 01 Manifest (locked)

`D-S040-E32-M` = **2,3,1,1** — full product pack; full F7 VONA surface; interview UI N/A; close 01 → 02.
