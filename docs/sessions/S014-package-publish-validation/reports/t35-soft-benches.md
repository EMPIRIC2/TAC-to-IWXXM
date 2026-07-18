# T3.5 — Soft benches vs lxml (E10-35)

**Session:** S014 / EV-010  
**Task:** T3.5  
**Date:** 2026-07-18  

## Deliverables

| Item | Path |
|------|------|
| Gate helpers | `scripts/bench/perf_gates.py` |
| Soft + hard-path tests | `tests/perf/test_t35_native_validate_soft_benches.py` |
| Baseline wiring | `perf-baselines.yaml` → `native_soft_bench` |
| Hard env flip | `IWXXM_VALIDATE_HARD_PERF=1` (T6.6) |

## Behaviour

- **Soft (build):** over-ceiling → `UserWarning` (`SOFT PERF: …`); test stays green.
- **Hard (publish):** same check + env → `AssertionError` (`HARD PERF: …`).
- Head-to-head uses **2023-1** vendor METAR example (fair Schematron comparison).

## Local evidence (dev wheel)

Soft warnings observed (expected on unoptimized maturin develop):

- `native_xsd_vs_lxml` — native slower (debug XSD compile path)
- `native_schematron_vs_lxml` — native real SCH vs cheap lxml skip
- `native_validate_vs_lxml` / committed lib_path ceiling — same

Hard-gate path asserted green (`test_hard_gate_path_wired_for_publish`,
`test_hard_mode_raises_on_over_ceiling`).
