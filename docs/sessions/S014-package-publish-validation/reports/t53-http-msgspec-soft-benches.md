# T5.3 — Soft HTTP msgspec bench (E10-35)

**Session:** S014 / EV-010  
**Task:** T5.3  
**Date:** 2026-07-19  
**Status:** completed

## Pass criteria

| Check | Mode |
|-------|------|
| msgspec encode p95 <= 1.0x same-run pydantic `model_dump_json` | Soft warn |
| `msgspec_json_response` vs committed `http_pydantic_map` ceiling | Soft warn |
| `IWXXM_VALIDATE_HARD_PERF=1` hard-fail path | Wired for T6.6 |

## Test

`tests/perf/test_t53_http_msgspec_soft_benches.py` — 6 passed

## Docs

`perf-baselines.yaml` — `http_soft_bench` section added

## Next

**T5.4** — Vitest / OpenAPI-derived FE type updates for breaking shapes
