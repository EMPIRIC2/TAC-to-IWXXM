# Laptop convert spike (non-authoritative)

> 2026-08-08 — local macOS only. **Do not** use as PR baselines.
> Authoritative baselines: CI ubuntu-latest → `tests/perf/baselines/converter_pr.yaml` (M1 T1.3).

| Product | p50 (s) | p95 (s) | n | warmup |
|---------|---------|---------|---|--------|
| METAR | 1.38e-5 | 1.57e-5 | 50 | 5 |
| SPECI | 1.53e-5 | 1.64e-5 | 50 | 5 |
| TAF | 8.37e-6 | 8.93e-6 | 50 | 5 |

Method: pure-Python `tac2iwxxm.convert`, profile `annex3`, `iwxxm_version=2025-2`.
