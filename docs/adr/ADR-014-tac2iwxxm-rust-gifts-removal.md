# ADR-014: Rust/PyO3 Acceleration, Expanded F6 Products, and GIFTs Removal

> **Status**: Accepted  
> **Date**: 2026-07-12  
> **Deciders**: User (S008 01-requirements AskQuestion)  
> **Stage**: 01-requirements  
> **Supersedes (partial)**: [ADR-013](ADR-013-tac2iwxxm-package-architecture.md) (Cython path; gifts-as-fallback; FAA-five-only v1)  
> **Deprecates**: [ADR-004](ADR-004-manual-gifts-sync.md), REQ-014  
> **Context refs**: [Context: general-tac-iwxxm-converter](../context/general-tac-iwxxm-converter.md), session S008

## Context

ADR-013 accepted `packages/tac2iwxxm` with pure Python v0, optional Cython lexer, FAA five
products, gifts retained as Annex-3 reference/fallback, and IWXXM-US vendor pin.

S008 requirements interview amended those choices: Rust/PyO3 instead of Cython; v1 product set
expanded to FAA five **plus VAA and TCA**; hard API cutover with **deletion of `packages/gifts`**
in the same PR that first wires tac2iwxxm to `POST /api/v1/convert`; package license **MIT**;
UI product/profile pickers in v1; metrics library/CI-only (no convert-response metrics fields).

## Decision

1. **Native acceleration**: Keep **pure Python v0** first. Optional hotspots use **Rust via
   PyO3** (not Cython). Benchmark harness must justify before shipping native wheels.
2. **F6 v1 products**: AIRMET, METAR, SIGMET, SPECI, TAF, **VAA**, **TCA** (seven). Delivery
   phases F6.a–F6.f (see `[Corpus: product]`).
3. **Cutover**: When any tac2iwxxm convert path is wired to `/api/v1/convert`, the API **must
   not** call gifts; **remove `packages/gifts`** in that same PR (hard cutover + delete).
4. **F1**: Status **Superseded by F6** (UX/actions remain user-facing until F6 UI lands; engine
   is tac2iwxxm).
5. **REQ-014 / ADR-004**: **Deprecated** — no in-repo gifts package to sync.
6. **License**: `packages/tac2iwxxm` is **MIT**.
7. **Unchanged from ADR-013**: New package (not gifts rewrite); IWXXM-US vendor pin; IR +
   product/profile plugins; default profile `annex3`; extend `/api/v1/convert` with `product` +
   `profile`; template `static+api` library under `packages/`.

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | Keep Cython (ADR-013) | User chose Rust/PyO3 ecosystem |
| 2 | Dual-run gifts until parity | User chose hard cutover + delete in first wire-up PR |
| 3 | FAA five only | User included VAA + TCA in v1 |
| 4 | Metrics on convert API response | User chose library/CI metrics only |

## Consequences

### Positive

- Single converter package ownership; no dual-engine maintenance after cutover
- Rust/PyO3 aligns with high-performance native extension practice while Python owns policy
- Broader product coverage matches gifts historical surface (VAA/TCA) plus FAA/US scope

### Negative / risks

- **Cutover risk**: Deleting gifts in the first wire-up PR means METAR/SPECI production path
  depends on tac2iwxxm correctness immediately — M-parity and golden suite must gate that PR
- Larger v1 scope (7 products + US profile + UI pickers)
- Rust toolchain in CI (maturin/cargo) when native extras land — detail in 04-tech-plan

### Follow-ups

- 01: Spec / UJ / test-plan / API contract deltas
- 04: PyO3 layout, gifts removal task list, iwxxm-us pin URL/tag
- Update plan-adherence / template rules when gifts path is removed from approved tree

## References

- ADR-013, ADR-004, REQ-014
- [docs/feature-list.md](../feature-list.md) F6
- Session S008-general-tac-iwxxm-converter
