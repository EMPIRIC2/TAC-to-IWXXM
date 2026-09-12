# T3.8a — Backend `/validate` Rust SDK + no double heavy-layer (F11.4 / F13)

**Session:** S014 / EV-010  
**Task:** T3.8a  
**Date:** 2026-07-18  
**Status:** completed (green via T3.8)

## Pass criteria

| Check | How |
|-------|-----|
| Bind Rust SDK | `api.iwxxm_validate_fn is validate_iwxxm` |
| SDK called | `/api/v1/validate` invokes SDK once with xsd+schematron |
| No double heavy | Orchestrator `validate_complete` layers exclude `XML_SCHEMA` / `SCHEMATRON` when SDK ran them |

## Test

`apps/backend/tests/unit/test_tc_f11_validate_rust_sdk.py`

## Next

**T3.8** — wire `validate_iwxxm` + dedupe orchestrator layers.
