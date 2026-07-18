# T3.8 — Wire `/validate` (+ convert validate) to `validate_iwxxm` (F11.4 / F13)

**Session:** S014 / EV-010  
**Task:** T3.8  
**Date:** 2026-07-18  
**Status:** completed  

## Changes

| Area | Change |
|------|--------|
| Bind | `from iwxxm_validate import validate_iwxxm as iwxxm_validate_fn` |
| `/validate` | After SDK run, strip `XML_SCHEMA` / `SCHEMATRON` from orchestrator layers |
| Convert + validate | SDK runs xsd+schematron; orchestrator skips those heavy layers |

## Tests

`apps/backend/tests/unit/test_tc_f11_validate_rust_sdk.py` (T3.8a) — green.

## Next

**T3.9** — optional `iwxxm-validate` CLI smoke.
