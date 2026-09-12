# S029 — SIGMET decode residuals (F9 deepen)

**Evolve:** EV-022  
**Branch:** `feat/EV-022-sigmet-decode-residuals`  
**Status:** implementation ready (local tests green)

## Scope

Teach `decode_tac` SIGMET/AIRMET explainers to cover WMO A6-1a tokens that were
residual while convert already succeeded: sequence, VALID, MWO (`YUSO-`), FIR
name, SE-box geometry, FL, MOV direction/speed.

## Changes

- `packages/tac2iwxxm/src/tac2iwxxm/decode.py` — richer `_explain_sigmet_airmet`
- `packages/tac2iwxxm/src/tac2iwxxm/glossary.py` — VALID / OF / AND / FIR/UIR
- `packages/tac2iwxxm/tests/test_tc_f9_sigmet_a6_decode_residuals.py`

## Verify

`uv run pytest packages/tac2iwxxm/tests/test_tc_f9_sigmet_a6_decode_residuals.py` + related decode suites — **62 passed**.
