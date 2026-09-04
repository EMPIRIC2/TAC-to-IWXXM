# ADR-038: ConversionProfile executable contract (spike #924)

> **Status**: Accepted (EV-924 / #924)  
> **Date**: 2026-09-03  
> **Deciders**: User (EV-924 evolve — contract accept, overlays defer)  
> **Related**: [ADR-013](ADR-013-tac2iwxxm-package-architecture.md), [ADR-036](ADR-036-semantic-vs-exchange-profiles.md), [ADR-030](ADR-030-dissemination-package-architecture.md)  
> **Issues**: [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Write-up**: session `reports/924-conversion-profile-contract.md` (EV-924)

## Context

Spike [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924) asks whether the conversion
profile should become an **executable deployment/conformance contract** (grammar, validation
rule-sets, mapper, output validation, optional dissemination defaults) including custom/operator
overlays ([#906](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/906) absorbed).

[ADR-036](ADR-036-semantic-vs-exchange-profiles.md) already split **semantic** and **exchange**
profile kinds and shipped nested HTTP wire fields. The monorepo implements behavior through:

- `tac2iwxxm.profile_registry` + emit plugins
- `tac-validate` product rules + ADR-028 issue registry
- `iwxxm-validate` for output validation
- `dissemination.exchange_registry` + packaging for exchange overlays
- `docs/domain/profiles/catalog.yaml` as machine index

Constraints:

- Fail-closed unknown profile ids
- No dissemination credentials in profile objects (ADR-021/029)
- No browser-uploaded unsigned schema bundles
- #924 is investigation-only — no runtime engine rewrite

## Decision

1. **Accept a normative ConversionProfile contract** as standing documentation. The contract
   **composes** ADR-036 semantic + exchange fields; it does **not** merge them into one wire enum.

2. **Implementation model (M5 / this spike):** behavior remains **code plugins + registries +
   catalog.yaml**. The contract is the **map**, not a new runtime loader.

3. **Contract field ownership**

   | Field group | Owner package / doc |
   |-------------|---------------------|
   | `id`, `appliesTo.products` | `docs/domain/profiles/catalog.yaml` |
   | `input.*`, `conversion.*` | `packages/tac2iwxxm` emit plugins |
   | `validation.tac` | `packages/tac-validate` + ADR-028 registry |
   | `validation.canonical` / staged pipeline | Deferred to #925 |
   | `outputValidation` | `packages/iwxxm-validate` + vendor pins |
   | `dissemination.exchangeProfile` | `packages/dissemination` (defaults only) |
   | `dissemination.defaultDestinations` | **Excluded** — BYOC memory-only |

4. **Custom / operator overlays (#906):** **Deferred** to #933 ConversionProfile editor evolve
   cycle. v1 trust model = **first-party catalog entries only**; unknown ids rejected.

5. **catalog.yaml schema v2 (Planned):** incrementally add contract fields already factual in
   repo (products, vendor_pins, implementation refs). No big-bang manifest migration in #924.

6. **OpenAPI:** keep ADR-036 nested `semantic_profile` / `exchange_profile` / `iwxxm_version` /
   `extensions`. Optional future shorthand `conversionProfile=` documented in api corpus only
   after #933 — not authorized by this ADR.

## Normative contract sketch

```yaml
ConversionProfile:
  id: US_FAA_NWS
  kind: semantic          # semantic | exchange (ADR-036)
  appliesTo:
    products: [METAR, SPECI, TAF, SIGMET, AIRMET]
  input:
    grammar: { implementation: tac2iwxxm/profiles/iwxxm_us }
    units: { policy: FAA_FMH1 }
  validation:
    tac: { registry: tac-validate, profile_emit_key: iwxxm_us }
  conversion:
    iwxxmVersion: independent   # HTTP field — not derived from id
    mapper: { emit_key: iwxxm_us }
    extensionSchemas: [IWXXM_US_3]
  outputValidation:
    engine: iwxxm-validate
  dissemination:              # optional defaults — not credentials
    exchangeProfile: GLOBAL_AFS
```

Exchange-only profiles (`GLOBAL_AFS`, …) use `kind: exchange` and omit conversion/input blocks.

## Alternatives considered

| # | Alternative | Why rejected / deferred |
|---|-------------|-------------------------|
| A | Runtime profile loader executing declarative RuleSet[] now | Premature vs #925; code plugins already work |
| B | Browser operator pack upload | Trust/SSRF — reject |
| C | Reject contract — keep ad hoc plugins only | Loses #922 platform narrative; catalog already partial contract |
| D | **Contract doc + deferred loader** | **Accepted** |

## Consequences

### Positive

- #924 acceptance criteria met without risky engine rewrite
- Clear field ownership for #925 / #933 follow-ons
- ADR-036 remains authoritative; ADR-038 extends without contradiction

### Negative / follow-ups

- Contract fields not yet machine-validated against runtime — #933 or #925 may add loader
- `appliesTo.stations` / state filters unimplemented — document as future

### Amend (EV-933 / #933 — Accepted)

Operator-scoped **signed overlays** are persisted on product Postgres (`DATABASE_URL`) with
JWT ownership (`user_id` = Auth `sub`). Trust model:

1. Client submits overlay body JSON over JWT (no client-supplied signature).
2. Server canonicalizes the body, computes **HMAC-SHA256** with
   `PROFILE_OVERLAY_HMAC_SECRET` over `user_id:base_profile_id:canonical_json`, and stores
   the hex digest.
3. Reads and convert apply **re-verify** the HMAC; missing or mismatched signature → 400.
4. Convert accepts optional multipart `overlay_id`. When set, Bearer JWT is required and
   ownership (or `shared=true`) is enforced; guests without `overlay_id` keep public convert.
5. First-party catalog entries remain the default trust root. Unsigned browser-uploaded
   schema/rule packs stay **rejected**. Overlay bodies must not carry credentials or
   destination URIs (ADR-021 / ADR-029).

See [Context: conversion-profile-editor-933](../context/conversion-profile-editor-933.md).

## References

- [Context: conversion-profile-contract-924](../context/conversion-profile-contract-924.md)
- [Context: conversion-profile-editor-933](../context/conversion-profile-editor-933.md)
- [ADR-037](ADR-037-platform-logical-layers.md) Profiles layer
- EV-924 session report `924-conversion-profile-contract.md`
- EV-933 / #933 F7.w / UJ-072
