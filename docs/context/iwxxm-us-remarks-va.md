# Scoped context — iwxxm-us-remarks-va (S032 / EV-025)

**Mode:** scoped · **Date:** 2026-07-31  
**Status:** completed (EV-025 closed; #809 residual → [va-multi-location-809](va-multi-location-809.md))  
**Session:** S032-iwxxm-us-remarks-va · **Cycle:** EV-025  
**Issues:** #810, #811, #812 closed; #809 open (soft shipped)

## Problem

S031 / EV-024 mined IWXXM-US METAR/SPECI model docs (#773) and filed encode children. Most US
extension types remain ❌ encode / ❌ fixture. Separately, `#804` wired
`sigmet-multi-location-VA` as **WMO reference** only — convert M-golden equality deferred (#809).
Soft-compare shipped in #816; residual equality/`wmoPass` tracked in
[Context: va-multi-location-809](va-multi-location-809.md).

## Runtime SoT

`vendor/manifest.json` → `vendor/schemas/iwxxm/2025-2/` + `vendor/schemas/iwxxm-us` **3.0**.

## Prior art (do not restart)

| Artifact | Use |
|----------|-----|
| `docs/domain/mining/iwxxm-us-metar-speci-pdf-mining-notes.md` | Type × TAC × encode checklist |
| `docs/domain/mining/fmh1-2019-mining-notes.md` | TAC RMK syntax |
| S031 gap list | Child map #809–#812 |
| `vendor/schemas/iwxxm/2025-2/IWXXM/examples/sigmet-multi-location-VA.{tac,xml}` | #809 peer |
| F15 / F20 / F23 quality cycles | Existing METAR/SPECI/VA encode patterns |

## Success

1. Every dig-checklist ❌ US type has lint (as needed) + encode + golden + validate smoke, or an
   explicit deferred child with rationale.
2. #810 / #811 / #812 acceptance checkboxes closable.
3. #809 soft→strict path documented; `wmoPass` only when ADR-032 equality holds.
4. US content never appears in WMO sample menu (UJ-039).

## Skills

Standard evolve build path (01→02→04→07…). Dig/PDF extract already done — re-open `.local/`
extract only if encode needs fresh PDF samples (do not commit PDF).
