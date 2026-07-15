# Source classes → destinations

Prefer sources in this order for **normative** claims. Always record access friction.

**Contradictions:** within a claim class, **defer to the latest** published/effective
edition or pin — see `SKILL.md` §Conflict resolution. Informative never overrides
normative SARP/schema/registry; vendor pin wins for runtime encode/validate.

| Class | Examples | Default label | Primary `docs/domain/` target | Notes |
|-------|----------|---------------|--------------------------------|-------|
| **WMO IWXXM schemas** | `wmo-im/iwxxm`, `schemas.wmo.int/iwxxm/<ver>/` | normative-schema | **canonical** `IWXXM_VALIDATION.md` + `IWXXM_CONVERSION.md` | Pin from `vendor/manifest.json`; digs → `mining/` |
| **TAC→XML guidance / examples** | `TAC-to-XML-Guidance.txt`, `…/examples/` | normative-conversion-notes / normative-examples | **canonical** `IWXXM_CONVERSION.md` | Includes `translationFailedTAC` shapes |
| **WMO Codes Registry** | `codes.wmo.int`, `iwxxm` / `49-2` / `306` / `common` | normative-vocabulary | `rules/RULE_SOURCE_URLS.md` + canonicals | Machine SoT for `xlink:href` / nilReason |
| **Codelist RDF repo** | `wmo-im/iwxxm-codelists` | normative-vocabulary | same | Feeds codes.wmo.int; vendor pin `49-2` |
| **UML / modelling** | `wmo-im/iwxxm-modelling` | informative (unless published as SoT) | **transitory** `mining/*-mining-notes.md` | Cite published schemas for runtime |
| **Translation fixtures** | `wmo-im/iwxxm-translation` | informative | `IWXXM_CONVERSION.md` (fixtures section) | README: no official WMO/ICAO status |
| **AHL / exchange** | community.wmo.int AHL page | normative-exchange | `rules/RULE_SOURCE_URLS.md` (+ bulletin in conversion) | TAC vs IWXXM `T1T2` |
| **Manual on Codes** | WMO-No. 306 Vol I.1 / I.3 | normative | **transitory** `mining/` → promote to canonicals | PDF → extract-pdf-to-repo |
| **ICAO Annex 3 / Docs** | Annex 3, Doc 8896, 10003, 9766 | normative | **canonical** `TAC_VALIDATION.md` (ops prose may also touch conversion) | **Paywall** — landings + section cites only |
| **National US** | FMH-1, `iwxxm-us`, codes.nws.noaa.gov | normative (national) / normative-schema | `RULE_SOURCE_URLS.md` + `TAC_VALIDATION.md` (`iwxxm_us`) | Separate from annex3 profile |
| **Historical GIFTs** | old fork / `packages/gifts` | historical-GIFTs | gap columns in `COVERAGE_MATRIX.md` only | ADR-014 — never ongoing SoT |
| **Community blogs / random mirrors** | third-party PDFs | informative or reject | dig only if useful; do not promote without label | Do not treat as normative |

**Never** write rule-provenance digs into `docs/domain/iwxxm/` or `docs/domain/validation/`
(those trees are ops / engine notes).

## Role tags (use in catalog rows)

| Role | Means |
|------|--------|
| `validation` | TAC syntax / template / business rules for input |
| `conversion` | TAC → IWXXM field / nilReason / href encoding |
| `iwxxm-validation` | XSD + Schematron (+ codelist) on output XML |
| `bulletin` | AHL / COLLECT / AMHS filename / multi-report wrap |

## F6 products (minimum coverage set)

`METAR` · `SPECI` · `TAF` · `SIGMET` · `AIRMET` · `VAA` · `TCA`

Optional IWXXM family (document if mined): `VONA` · `SWX` · `WAFS` · `QVACI`.

## Related vendor paths (read-only)

```
vendor/manifest.json
vendor/schemas/iwxxm/
vendor/schemas/iwxxm-codelists/
vendor/schemas/iwxxm-translation/
vendor/schemas/iwxxm-us/
vendor/schemas/iwxxm-modelling/
```
