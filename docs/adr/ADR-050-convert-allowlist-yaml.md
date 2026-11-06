# ADR-050: Convert allowlist lives in package YAML

## Status: Accepted

[Corpus: product §F6] [Corpus: system-spec] [Corpus: adr/ADR-047]

## Context

`convert()` rejected national advisory products from frozensets in `packages/tac2iwxxm/src/tac2iwxxm/convert.py`. `docs/domain/profiles/catalog.yaml` lists `products` as well, and those lists had drifted. The next country product should be a catalog row, not a new Python module. A published wheel must not read the docs tree.

## Decision

The runtime convert allowlist is `packages/tac2iwxxm/src/tac2iwxxm/conf/convert_allowlist.yaml`, keyed by emit key and loaded with Hydra (`hydra-core`). Annex 3 is not gated there, so every supported product stays allowed. `compose_allowlist` accepts Hydra overrides for local checks. `make convert-allowlist` and `scripts/tac2iwxxm/compose_convert_allowlist.py` print the composed file. A drift test keeps the YAML aligned with `catalog.yaml` `products` for the gated keys. Emit stays on the existing ADR-047 maps. United States VAA adds `iwxxm_us` to `annex3-vaa.yaml`. India TCA adds `in_imd` to `annex3-tca.yaml`.

## Consequences

Adding a product for an existing profile edits the YAML and the catalog row, plus a fixture test. United States TAF stays on the allowlist. Canada SIGMET and VAA stay as they already convert. Lint profiles are unchanged.

## Alternatives Considered

- Keep the Python frozensets and only append products. The next country product would still be a code edit.
- Read `docs/domain/profiles/catalog.yaml` at runtime. The wheel would depend on the docs tree.
