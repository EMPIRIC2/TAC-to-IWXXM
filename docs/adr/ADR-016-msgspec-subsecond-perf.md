# ADR-016: msgspec in Packages, Pydantic at HTTP, Sub-Second Perf Gates

> **Status**: Accepted  
> **Date**: 2026-07-12  
> **Deciders**: User (S008 04-tech-plan Q1–Q2, Q6, Q9, Q11)  
> **Stage**: 04-tech-plan  
> **Related**: ADR-015, dependency-inventory.md  
> **Session**: S008-general-tac-iwxxm-converter

## Context

`tac2iwxxm` and `tac-validate` need structured IR / issue models. Backend HTTP already uses
pydantic. The user requires **sub-second** performance for typical single-report lint, convert,
and validate paths, and asked to prioritize msgspec.

## Decision

1. **Package layout**: `src/` layout for `tac2iwxxm`, `iwxxm-validate`, `tac-validate` (Q1=A).
2. **Serialization**: **msgspec.Struct** for package IR and issue models; reuse
   `msgspec.json.Encoder` / `Decoder` instances on hot paths ([msgspec perf tips](https://msgspec.dev/perf-tips.html)).
3. **HTTP boundary**: FastAPI continues to use **pydantic**; map msgspec → pydantic DTOs at
   router edges (Q2=B, Q9=C).
4. **Bulletin / lint issues**: Include lint-style `issues[]` and optional `fixes[]` when rules
   can suggest repairs (Q6).
5. **Perf gates (Q11=C)**: Separate pytest benchmarks for (A) lint | convert | validate alone
   and (B) lint→convert→Schematron library path. Soft-fail until cutover; **hard-fail** as a
   cutover gate (with ADR-017 PyO3).

## Alternatives Considered

| # | Alternative | Why rejected |
|---|-------------|--------------|
| 1 | pydantic everywhere | User prioritized msgspec for sub-second |
| 2 | dataclasses only | Weaker validation/encode performance vs msgspec Structs |
| 3 | Soft benches forever | User chose hard gate at cutover |

## Consequences

- New runtime dep `msgspec` on two packages; license audit at add time.
- Router mapping layer must stay thin to preserve latency budget.
- Benchmark fixtures must be committed and stable.

## References

- D-S008-04-q1q5, D-S008-04-q6q10, D-S008-04-q11q15-provisional
- execution-plan.md (S008) Phase 1–3
