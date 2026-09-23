# ADR-049: Residual YAML — detector hatches, name enrichment, emit plugins

**Status:** Accepted  
**Date:** 2026-09-23  
**Session:** EV-1252-residual-yaml  
**Epic:** [#1252](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1252)  
**Corpus:** [Corpus: product §F6] [Corpus: product §F9] [Corpus: product §F15] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: adr/ADR-047] [Corpus: tests]

## Context

[#1226](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1226) rated every core product × engine cell **full**. Three named Python residuals remain and must stay honest in the product-engine matrix: TAC detector hatches, decode airport-name enrichment, and convert emit-map `plugin:` builders. [#1252](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1252) deepens those residuals without Schematron-as-YAML, HTTP YAML bodies, or in-app authoring (ADR-044).

## Decision

1. **Detector hatches** — Declarative detector YAML is the source of truth for hatch behavior (`hatch_r1_order`, `hatch_r3`, `hatch_r4_membership`, `hatch_r5_pk_and_extension`, and product hatches `hatch_taf` / `hatch_sigmet` / `hatch_airmet` / `hatch_vaa` / `hatch_tca`). `kind: python` remains only when a rule cannot be expressed in the detector DSL. An overlay that changes a formerly hatched check must change the lint result in a fixture.

2. **Decode enrichment** — A file/env YAML ICAO→name table is the source of truth for airport names on decode. `set_location_name_resolver` stays an optional override (live lookup may still win when installed). Public `decode_tac` keys do not change. A miss stays designator-only.

3. **Emit plugins** — Python XML builders stay the constructors. Emit-map YAML remains the router (`plugin:`). Each product family needs a golden that shows swapping `plugin:` changes IWXXM output. This cycle does not add a declarative XML language. ADR-047 cells stay **full**.

4. **Boundaries** — File/env overlays only (ADR-045 / ADR-047). No HTTP pack, policy, or emit YAML. No operator UI. H4–H5 N/A. Public `convert` and `decode_tac` wire stay stable.

5. **Delivery** — Three child issues, one pull request each, in session EV-1252-residual-yaml. Implementation waits until the Spec→Build gate is open.

## Consequences

- Honesty matrix notes point here. A **full** cell rating does not mean these residuals are already declarative.
- Detector DSL may gain kinds. Each new kind needs a fixture and a note when a hatch is retired.
- Name-table overlays must not require network access.
- Emit goldens prove routing, not that builders became data.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Leave hatches as Python and only name them from YAML | Rejected for detectors (D6): behavior must move into declarative rules where the DSL can express it |
| YAML documents the resolver and leaves it as source of truth | Rejected for enrichment (D7): the table is the source of truth; the hook is an override |
| Declarative XML for every profile, or Annex 3 METAR/SPECI only | Rejected for emit (D8): builders stay; overlay swap of `plugin:` is the configurability |
