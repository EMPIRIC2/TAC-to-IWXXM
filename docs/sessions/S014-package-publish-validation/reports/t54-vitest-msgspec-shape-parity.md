# T5.4 — Vitest msgspec HTTP shape parity (E10-18 / TC-F11-001)

**Session:** S014 / EV-010  
**Task:** T5.4  
**Date:** 2026-07-19  
**Status:** completed

## Approach

No OpenAPI→TS codegen this cycle (P1 backlog). Vitest key-parity guards in
`apps/frontend/src/utils/api.test.ts` for convert / lint / decode / bulletin
against T5.1 backend contract smoke.

## Result

49 passed in `api.test.ts` (includes 4 new msgspec parity tests).

## Next

**T5.5** — align FE client types (`summary` required; optional `metadata`).
