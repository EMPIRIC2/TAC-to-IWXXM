# F11 hard-gate absolute baselines (T1.3 / E10-35)

> **Source matrix**: [`layer-cost-matrix.md`](./layer-cost-matrix.md)  
> **Harness**: `scripts/bench/validation_stack.py`  
> **Recorded**: 2026-07-18 (S014 / EV-010 / T1.3)  
> **Host note**: Single-process local `uv run` timings; re-record on CI publish runners
> before hard-fail cutover if hardware differs materially.

## Gate definitions (E10-35)

| Gate | Formula | Applies when |
|------|---------|--------------|
| Library path | candidate p95 ≤ **0.85 ×** `lib_path_lxml_baseline_p95_s` | Soft in build (T3.5); **hard** at publish/cutover (T6.6) |
| HTTP msgspec | msgspec encode p95 ≤ **1.0 ×** `http_pydantic_map_baseline_p95_s` | Soft in build (T5.3); **hard** at publish (T6.6) |
| Wheel smokes | install + import + sample convert/validate | Hard at publish (T6.6) |

## Absolute baselines (seconds, p95)

Values taken from the committed layer-cost matrix **mean p95 by layer**
(ok cells) and the **single_metar** composed library path.

| ID | Meaning | Absolute p95 (s) | Notes |
|----|---------|------------------:|-------|
| `lint_p95_s` | `tac_validate.lint` mean | 0.0000021 | Matrix mean p95 |
| `convert_ir_p95_s` | `tac2iwxxm.convert` mean | 0.0000218 | Matrix mean p95 |
| `xsd_p95_s` | `validate(..., levels=("xsd",))` mean | 0.0000364 | Matrix mean p95 |
| `schematron_p95_s` | Schematron cell mean | 0.0000352 | **Skip path** — see caveat |
| `http_pydantic_map_baseline_p95_s` | pydantic `model_dump_json` mean | 0.0000062 | **1.0×** HTTP gate denominator |
| `http_msgspec_observed_p95_s` | msgspec encode mean (reference) | 0.0000020 | Already &lt; 1.0× pydantic |
| `lib_path_lxml_baseline_p95_s` | lint + convert + xsd + schematron (means) | 0.0000955 | **0.85×** lib gate denominator |

### Derived hard ceilings

| Ceiling ID | Formula | Absolute (s) |
|------------|---------|-------------:|
| `lib_path_hard_ceiling_p95_s` | `0.85 * lib_path_lxml_baseline_p95_s` | 0.000081175 |
| `http_msgspec_hard_ceiling_p95_s` | `1.0 * http_pydantic_map_baseline_p95_s` | 0.0000062 |

## Machine-readable copy

See [`perf-baselines.yaml`](./perf-baselines.yaml) — import from T3.5 / T5.3 / T6.6 tests.

## Soft benches (T3.5)

| Check | Mode | Hard path |
|-------|------|-----------|
| Native `validate_iwxxm` p95 ≤ **0.85×** same-run lxml `validate` (xsd / schematron / combined) | Soft warn in build | `IWXXM_VALIDATE_HARD_PERF=1` → assert (T6.6) |
| Native validate vs committed `lib_path_lxml` ceiling | Soft warn | same env flip |
| Helpers | `scripts/bench/perf_gates.py` | `tests/perf/test_t35_native_validate_soft_benches.py` |

Native Schematron is **real evaluation**; lxml may still `SCHEMATRON_SKIPPED` — soft
warnings on Schematron ratio are expected until publish re-baseline.

**2026-07-18 T3.5 local run (maturin `dev` / unoptimized):** native XSD+combined
soft-warned at ~50–60× same-run lxml (debug build + full Schematron vs skip path).
Treat as wiring proof only — **re-bench release wheels** before T6.6 hard-fail.

## Caveats (must carry into hard gates)

1. **Schematron XSLT2 skip** — `2025-2` lxml path returns `SCHEMATRON_SKIPPED`
   (D-S008-T21-sch). `schematron_p95_s` and therefore `lib_path_lxml_baseline_p95_s`
   **understate** true Schematron cost. Re-baseline after F13 Rust Schematron (T3.3/T3.5)
   before treating the 0.85× gate as meaningful for Schematron.
2. **XSD import gap warning** — non-blocking GML substitutionGroup noise on 2025-2;
   does not invalidate relative encode benches.
3. Soft benches during M1–M5 may warn; only T6.6 / publish tags hard-fail against these
   ceilings (unless a later decision tightens earlier).
