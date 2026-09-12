# T6.6 — Hard publish gates (E10-35)

> **Session:** S014 / EV-010  
> **Date:** 2026-07-19  
> **Host:** local `uv run` after `maturin develop --release` (iwxxm-validate)  
> **Status:** **PASS** (head-to-head XSD + combined; HTTP; wheels)  
> **Decision:** D-S014-EV010-t66-lib-gate option 3 — optimize native to 0.85× before tags

## Fix (T6.6 optimization)

**Root cause:** Rust `validate_document` re-parsed the full IWXXM/GML XSD graph on every
call; lxml caches via `@lru_cache`.

**Change:** Process-wide caches in `packages/iwxxm-validate/rust/src/lib.rs`:

- `Arc<XsdSchema>` keyed by `(xsd_path, sorted catalog_roots)`
- `Arc<SchematronSchema>` keyed by `sch_path`
- Basename index for `VendorResolver` (depth-6 walk once per catalog set)
- Per-parse resolve memoization
- `clear_schema_caches()` for tests

Cold native XSD ≈ 0.10s → warm ≈ 0.0004–0.0006s on this host.

## Gate definitions

| Gate | Formula | Result |
|------|---------|--------|
| Library XSD | native p95 ≤ **0.85 ×** same-run lxml XSD | **PASS** (obs ~0.03×) |
| Library combined | native XSD+SCH ≤ **0.85 ×** lxml XSD+SCH | **PASS** (obs ~0.03×) |
| HTTP msgspec | msgspec encode p95 ≤ **1.0 ×** pydantic map | **PASS** |
| Wheel smokes | clean-venv install + convert/validate/CLI | **PASS** |

## Release-build measurements (post-cache, 2026-07-19)

`IWXXM` fixture: vendor `2023-1` `metar-A3-1.xml`. Native: release PyO3 + schema cache.
Iterations: 11 (lib) / 51 (HTTP). Warmup fills caches (same as soft benches).

| Check | Candidate p95 (s) | Baseline p95 (s) | Observed ratio | Ceiling | ok |
|-------|------------------:|-----------------:|---------------:|--------:|:--:|
| `native_xsd_vs_lxml` | 0.000427 | 0.015022 | **0.028** | 0.0128 | ✓ |
| `native_validate_vs_lxml` | 0.000300 | 0.011585 | **0.026** | 0.00985 | ✓ |
| `native_schematron_vs_lxml` | 0.000373 | 0.000118 | **3.16** | 0.000100 | ✗\* |
| `http_msgspec_vs_pydantic_map` | — | — | **&lt;1.0** | 1.0× | ✓ |

\* Schematron-only vs lxml remains unfair: lxml returns `SCHEMATRON_SKIPPED` for
`queryBinding="xslt2"` (D-S008-T21-sch) while native evaluates real rules. Soft benches
keep `hard=False` for this row. **T6.6 hard path** asserts XSD + combined only
(`IWXXM_VALIDATE_HARD_PERF=1` → `test_t66_lib_hard_gates_under_env_flip` **PASS**).

## Wheel smokes (UJ-DEV-005)

| Test | Result |
|------|--------|
| `packages/tac-validate/tests/test_tc_f12_wheel_smoke.py` | **PASS** |
| `packages/tac2iwxxm/tests/test_tc_f14_002_validate_extra.py` | **PASS** |
| `packages/iwxxm-validate/tests` | **76 passed**, 1 skipped |

## PyPI tags (UJ-023)

Still **BLOCKED** — Trusted Publisher ×3 not configured (operator). Perf hard gates no longer block tagging.

## Verdict

| Slice | Verdict |
|-------|---------|
| F11 HTTP hard (1.0×) | **PASS** |
| F12–F14 local wheel smokes | **PASS** |
| F13 lib hard (0.85× XSD + combined) | **PASS** after schema cache |
| Live PyPI tags | **BLOCKED** (Trusted Publisher only) |

**T6.6 hard publish gates satisfied** for E10-35 head-to-head XSD/combined + HTTP + wheels.
Pending: user approve close T6.6 → configure Trusted Publisher → tag publish (UJ-023).
