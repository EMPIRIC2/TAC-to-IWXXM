# ADR-017: PyO3 Required Before F6 Cutover (Amends ADR-014)

> **Status**: Accepted  
> **Date**: 2026-07-12  
> **Deciders**: User (S008 04-tech-plan Q12 / Q12b=A)  
> **Stage**: 04-tech-plan  
> **Amends**: [ADR-014](ADR-014-tac2iwxxm-rust-gifts-removal.md) §Decision (1) “pure Python v0 first; optional PyO3”  
> **Related**: ADR-016  
> **Session**: S008-general-tac-iwxxm-converter

## Context

ADR-014 allowed pure Python v0 with optional Rust/PyO3 after benches justified it. S008
04-tech-plan requires **full PyO3** for this work, and cutover must not proceed until native
extension and sub-second benches hard-pass.

## Decision

1. **PyO3 is required** for the F6 cutover PR (not optional).
2. Cutover (wire `/convert` → `tac2iwxxm`, delete `packages/gifts`, delete inline F2) is
   **blocked** until:
   - Required PyO3 hotspots ship and load in CI/API image;
   - ADR-016 Q11 benches **hard-pass**.
3. Pure Python implementations may exist during M3–M4 development but are not a cutover
   substitute.
4. CI gains maturin/cargo jobs when the crate lands (execution-plan T4.3–T4.5).

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Keep ADR-014 optional PyO3 | User Q12b=A |
| 2 | Cut over on Python, PyO3 later same phase | Rejected for hard gate |
| 3 | Defer all Rust to later session | Rejected |

## Consequences

- Longer path to cutover; Docker/API image must build native wheels.
- ADR-014 “pure Python v0 first” is superseded for **this session’s cutover gate**; historical
  text remains for context.
- Aggressive gifts delete (Q5=ii) still applies **after** this gate.

## References

- D-S008-04-q12b-q15c
- I-S008-04-pyo3-required (resolved)
- S008 execution-plan M4
