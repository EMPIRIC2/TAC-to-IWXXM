# Scoped context — package publish + validation stack

**Status:** active  
**Session:** S014-package-publish-validation / EV-010  
**Created:** 2026-07-18  
**Issues:** [#703](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/703),
[#699](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/699),
[#698](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/698),
[#693](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/693)

## R1 — Starting point in repo

| Package | Path | PyPI name (approved) | Today |
|---------|------|----------------------|-------|
| Converter | `packages/tac2iwxxm` | `tac2iwxxm` | msgspec IR; optional PyO3 (`maturin`); hatch wheel |
| TAC lint | `packages/tac-validate` | `tac-validate` | msgspec reports; thin rules |
| IWXXM validate | `packages/iwxxm-validate` | `iwxxm-validate` | lxml XSD + isoschematron; msgspec reports |

Vendor schemas live under `vendor/schemas/*` (read-only pins). Backend HTTP still pydantic
at edges ([ADR-016](../adr/ADR-016-msgspec-subsecond-perf.md)); user wants msgspec deeper
in backend internals this cycle (ADR amend expected).

## R2 — Domain corpus to mine into packages

Primary trees (not CORPUS standing docs — citation/provenance only):

- `docs/domain/validation/` — comprehensive layers, failure taxonomy, Schematron notes
- `docs/domain/rules/` — coverage matrix, rule source URLs
- `docs/domain/mining/` — WMO/ICAO/FMH mining notes
- `docs/domain/TAC_VALIDATION.md`, `IWXXM_VALIDATION.md`, `IWXXM_CONVERSION.md`

**Constraint:** no copyrighted full Annex 3 / FMH text in wheels — encode rules + cite sources.

## R3 — Official model asymmetry (#703)

| Side | Official machine model? |
|------|-------------------------|
| IWXXM XML | Yes — `iwxxm-modelling` UML→GML + published XSD/Schematron |
| TAC | No — prose + national dialects only |

Codegen spike targets IWXXM artefacts only.

## R4 — Publish path

Follow trusted-publishing / tag-driven release pattern
([Real Python](https://realpython.com/pypi-publish-python-package/)): build sdist+wheel,
smoke-install, publish on version tags. Three packages share CI patterns; schema bundle
size is a design risk for `iwxxm-validate`.

## R5 — Performance order of work

Per intake: **#703 benches/design first**, then deepen #698 / #699 / #693. Schematron in
Rust is designed fully this cycle; implementation is time-boxed against measured L5 cost.
