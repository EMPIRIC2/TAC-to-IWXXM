# Bug report: convert METAR gate blocks F6 products

**ID:** BUG-2026-07-12-convert-metar-gate-blocks-f6  
**Date:** 2026-07-12  
**PR:** #710  
**Session:** S008 / EV-006 / PRM-014

## Error description

F6.e UI pickers send `product=TAF` (and other non-METAR products) to `POST /api/v1/convert`, but the endpoint still runs `ValidationService.validate_all_layers()`, which requires a METAR/SPECI keyword. Conversion never reaches `tac2iwxxm`.

## Error logs

```
VALIDATION_FAILED — Missing METAR/SPECI keyword
```

(Reproduced via Bugbot on PR #710; live probe with unknown product previously succeeded only because product was ignored.)

## Investigation

1. T8.2 forwards `product`/`profile` into `convert_metar_tac_with_metadata`.
2. Manual and file convert loops still call `validate_all_layers` unconditionally.
3. `services/validation.py` fails TAC without `\b(METAR|SPECI)\b`.

**Root cause:** METAR-era pre-check not product-gated after F6.e wiring.

## Repro test

- Path: `apps/backend/tests/unit/test_bug_2026_07_12_convert_metar_gate_blocks_f6.py`
- Status: red until fix; green after product-gated skip

## Fix

Skip `validate_all_layers` when multipart `product` is not METAR or SPECI.
