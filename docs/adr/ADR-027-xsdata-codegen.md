# ADR-027: XSD codegen via xsdata (+ pydantic plugin)

## Status: Accepted

## Context

F11 requires production codegen from published IWXXM **XSD** (UML = provenance only), with
CI regeneration on vendor pin bumps (E10-23). Options considered: selective custom generator
targeting msgspec/Rust for hot-path speed, vs **xsdata** for full schema→Python models.

User priority for 40″: efficacy of typed models from authoritative XSDs; validation/translation
**runtime** speed remains owned by Rust XSD+Schematron (F13) and msgspec IR convert (F6/F14),
not by full Python bind-on-validate.

## Decision

1. Use **[xsdata](https://github.com/tefra/xsdata)** with **[xsdata-pydantic](https://xsdata-pydantic.readthedocs.io/)**
   to generate **full Python (pydantic) models** from pinned IWXXM XSDs.
2. Keep **validate hot path** on Rust well-formed + XSD + Schematron (`packages/iwxxm-validate/rust`);
   do **not** require xsdata object graphs for `/validate` latency.
3. In-cycle **follow-on tasks** adapt generated models toward msgspec Structs and/or Rust types
   where convert builders benefit — adaptation is explicit tasks, not a silent rewrite of xsdata output.
4. Codegen runs in CI when `vendor/manifest.json` pins change; outputs committed or regenerated
   in the same PR as pin bumps (execution plan M1/M3).

## Consequences

- New **dev/codegen** dependencies: `xsdata`, `xsdata-pydantic` (MIT) — listed in
  `docs/dependency-inventory.md`.
- Generated pydantic models coexist with ADR-026 msgspec HTTP responses and package msgspec IR;
  dual model families are intentional until adaptation tasks land.
- Wheel size / schema subset (E10-34) remains independent of codegen — runtime bundle ≠ modelling tree.

## Alternatives Considered

| Option | Why not |
|--------|---------|
| Selective custom msgspec/Rust generator only | Stronger for pure speed; user chose xsdata completeness (40″B) |
| Skip codegen this cycle | Violates must-ship E10-11/23 unless kill-switch AskQuestion |
| xsdata dataclasses without pydantic plugin | Weaker fit with existing pydantic OpenAPI ecosystem |

## References

- E10-23, E10-40; F11; `docs/context/package-publish-validation.md` R3
- ADR-026 (msgspec HTTP); ADR-016 (package msgspec)
