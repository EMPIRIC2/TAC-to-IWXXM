# T5.5 — Frontend client types after msgspec HTTP (ADR-026)

**Session:** S014 / EV-010  
**Task:** T5.5  
**Date:** 2026-07-19  
**Status:** completed

## Changes

| Type | Change |
|------|--------|
| `ConversionResponse` | Additive optional `metadata` |
| `DecodeTacResponse.summary` | Required `string` (matches backend default `""`) |

Workbench call sites (`FileConverter`, `useLiveWorkbenchAssist`) unchanged —
JSON field names unchanged under msgspec `model_dump(mode="json")` encode.

## Next

**T5.6** — re-run H0c CORS policy suite.
