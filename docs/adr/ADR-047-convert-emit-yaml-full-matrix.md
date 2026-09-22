# ADR-047: Convert emit YAML + full engine matrix

**Status:** Accepted  
**Date:** 2026-09-21 (Accepted 2026-09-22 on M3 emit pilot / #1229)  
**Session:** EV-yaml-full-configurability  
**Epic:** [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226)  
**Corpus:** [Corpus: product §F2/F6/F9/F12/F15] [Corpus: adr/ADR-038] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: system-spec] [Corpus: tech-spec] [Corpus: tests]

## Context

[#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224) / [#1225](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1225) shipped honesty documentation and package overlay examples/preflight. Convert **emit** remains imperative Python plugins. Operators and SDK embedders need true **full** YAML configurability across TAC decode, TAC validation, IWXXM output policy, and TAC→IWXXM convert — including emit — without HTTP YAML injection or in-app authoring (ADR-044).

Vendor IWXXM **Schematron** remains the authoritative rule source (ADR-046). Application YAML must not re-author Schematron, but runtime must keep Schematron bundles aligned with the IWXXM **pin** used for emit and validate.

## Decision

1. **Emit map YAML** — Introduce a declarative mapping from convert IR / slots to IWXXM element builders or templates, keyed by conversion profile, product, and pin. Loaded as package-owned catalogs with file/env overlays (exact env name locked in Spec/Build). Composes with ADR-045 packs and ADR-038 profiles.

2. **Stable public API** — `tac2iwxxm.convert` and HTTP convert keep the same request/response shape. Emit engine is an internal implementation detail.

3. **Parity gate** — For each product advancing to emit-YAML: fixtures prove YAML emit matches or intentionally replaces the Python plugin. Plugins may remain as fallback until the honesty-matrix cell is rated **full**.

4. **Full engine matrix** — End-state: every core product (METAR, SPECI, TAF, SIGMET, AIRMET, VAA, TCA) × (decode pack, TAC quality policy, TAC detectors, IWXXM output policy, convert pack-IR, convert emit) = **full**, with CI evidence (builtin SoT + overlay behavior change + golden/fixture + matrix lock).

5. **Schematron pin match** — Schematron stays vendor SoT (not application-authored YAML). Convert and validate paths MUST assert that the Schematron bundle/version matches the IWXXM pin in use. Soft-preview may document exceptions only if Spec explicitly waives a path.

6. **Injection boundary** — Executable overlays remain file/env only. No HTTP pack/policy/emit YAML bodies. No in-app YAML authoring UI (ADR-044).

7. **Program shape** — Multi-milestone epic [#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226): M1 templates/DX → M2 METAR+SPECI full (minus emit) → M3 emit pilot METAR then SPECI → M4 remaining products (parallel PRs) → M5 all-full gate + pin↔SCH asserts.

## Consequences

- New Spec/Build program; PyPI packages gain starter templates and clearer overlay DX early (M1).
- Larger review surface when M4 advances products in parallel.
- Accept this ADR at Build gate open or on the first emit PR (M3); until then status remains **Proposed**. **Accepted** with METAR/SPECI emit-map routing (#1229).

## Alternatives considered

| Option | Why not |
|--------|---------|
| XML-only emit templates | Fragile vs schema/pin churn |
| XSD codegen-only emit | Heavy; couples tightly to vendor trees |
| HTTP YAML upload | Rejected (security / ADR-044 boundary) |
| Schematron-as-YAML | Rejected; vendor `.sch` remains SoT |

## Related

- Children: [#1227](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1227) M1 · [#1228](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1228) M2 · [#1229](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1229) M3 · [#1230](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1230) M4 · [#1231](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1231) M5
- [ADR-045](ADR-045-shared-tac-pack-engine.md) · [ADR-046](ADR-046-validation-policy-layers.md)
- Decisions: `docs/decisions/ev-yaml-full-configurability.md`
