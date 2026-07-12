# ADR-013: New `tac2iwxxm` Package with IWXXM-US Profile and FAA Five-Product v1

> **Status**: Partially superseded by [ADR-014](ADR-014-tac2iwxxm-rust-gifts-removal.md)  
> **Date**: 2026-07-12  
> **Deciders**: User (S008 AskQuestion)  
> **Stage**: 00-context  
> **Context refs**: [Context: general-tac-iwxxm-converter R1–R5](../context/general-tac-iwxxm-converter.md)  
> **Note**: Package + IWXXM-US pin + IR/plugins still stand. Cython path, gifts-as-fallback, and
> FAA-five-only v1 are superseded by ADR-014 (Rust/PyO3, gifts removal, +VAA/TCA).

## Context

The monorepo converts METAR/SPECI via `packages/gifts` (Annex 3 only; REMARKS stripped) and
validates against vendored WMO IWXXM Schematron/XSD. NOAA MDL IWXXM-US schemas supplement IWXXM
for FAA filed differences (AIRMET, METAR, SIGMET, SPECI, TAF) but are not present in
`vendor/schemas/`. The user wants a generalizable, NumPy-style (CPython + optional C/Cython)
converter library with accuracy metrics and format extensibility.

Constraints: REQ-014 (manual gifts upstream), REQ-016 (no product rewrite-as-migration),
template `static+api` (library under `packages/`, not a new deployable).

## Decision

1. **R1 — Package**: Create a new workspace package `packages/tac2iwxxm` (name finalizable in
   01-requirements). Keep `packages/gifts` as Annex-3 reference and optional fallback; do not
   rewrite gifts in place.
2. **R5 / R2 — Runtime**: Target is **CPython with optional C/Cython extensions** (NumPy pattern).
   Ship **pure Python v0** first; add Cython on the TAC lexer only after a batch benchmark harness
   proves need.
3. **R3 — v1 product scope**: Support the full FAA five in v1 — **AIRMET, METAR, SIGMET, SPECI,
   TAF** — each with Annex-3 body encoding plus IWXXM-US profile extensions where published.
4. **R4 — US schemas**: Pin IWXXM-US under `vendor/schemas/iwxxm-us` via `vendor/manifest.json`
   (same snapshot pattern as ADR-001 for wmo-im).

Architecture: Python API → IR → product plugins → profile plugins (`annex3` / `iwxxm_us`) →
XML writer → Schematron/XSD metrics. US types attach via IWXXM `extension` blocks (supplement,
not replace).

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Evolve `packages/gifts` in place | Breaks clean upstream merges (REQ-014) |
| 2 | Hybrid gifts body + thin US-only package | Splits IR; harder multi-product metrics |
| 3 | Cython from day one | Premature; Schematron/API dominate latency; correctness first |
| 4 | Rust/PyO3 | Extra toolchain; Cython closer to NumPy/CPython ecosystem choice |
| 5 | METAR/SPECI(+US) only for v1 | User chose full FAA five |
| 6 | Fetch IWXXM-US at runtime / skip vendor | Non-deterministic builds; weak offline CI (same rationale as ADR-001) |

## Consequences

### Positive

- Clear SoC: gifts remains mergeable; new package owns IR, US profile, multi-product plugins
- Vendor SoT for both WMO and US schemas enables reproducible Schematron/XSD gates
- Pure-Python v0 unlocks accuracy fixtures before native complexity
- Full FAA five aligns package mission with MDL IWXXM-US product set

### Negative / risks

- **Scope risk**: gifts has no SIGMET/AIRMET encoders; US AIRMET/SIGMET modeling docs are thinner
  than METAR/TAF in the provided corpus — 01/04 must phase delivery (shared IR first, then
  product plugins) without shrinking the accepted v1 *goal*
- Larger vendor tree; need a reliable upstream URL/tag for iwxxm-us
- Dual packages until API cutover; parity metrics vs gifts required for METAR/SPECI Annex-3

### Follow-ups

- 01-requirements: feature id (Fn), UJs, phased acceptance within v1 goal
- 04-tech-plan: manifest pin source for iwxxm-us, IR schema, metrics CI, Cython optional extra
- Scaffold `packages/tac2iwxxm` after evolve plan approval

## References

- [Context: general-tac-iwxxm-converter](../context/general-tac-iwxxm-converter.md)
- ADR-001 (vendor snapshots), ADR-004 (manual gifts sync)
- [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm)
- [MDL Data Modeling / IWXXM-US](https://vlab.noaa.gov/web/mdl/data-modeling)
- Session S008-general-tac-iwxxm-converter
