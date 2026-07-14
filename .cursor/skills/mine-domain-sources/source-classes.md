# Source classes → destinations

Prefer sources in this order for **normative** claims. Always record access friction.

| Class | Examples | Default label | Primary `docs/domain/` target | Notes |
|-------|----------|---------------|--------------------------------|-------|
| **WMO IWXXM schemas** | `wmo-im/iwxxm`, `schemas.wmo.int/iwxxm/<ver>/` | normative-schema | `iwxxm/IWXXM_VALIDATION_SOURCES.md` + `IWXXM_CREATION_SOURCES.md` | Pin tag from `vendor/manifest.json` |
| **TAC→XML guidance / examples** | `TAC-to-XML-Guidance.txt`, `…/examples/` | normative-conversion-notes / normative-examples | `iwxxm/IWXXM_CREATION_SOURCES.md` | Includes `translationFailedTAC` shapes |
| **WMO Codes Registry** | `codes.wmo.int`, `iwxxm` / `49-2` / `306` / `common` | normative-vocabulary | `RULE_SOURCE_URLS.md` + creation/validation companions | Machine SoT for `xlink:href` / nilReason |
| **Codelist RDF repo** | `wmo-im/iwxxm-codelists` | normative-vocabulary | same | Feeds codes.wmo.int; vendor pin `49-2` |
| **UML / modelling** | `wmo-im/iwxxm-modelling` | informative (unless published as SoT) | optional mining notes | Generation tooling; cite schemas for runtime |
| **Translation fixtures** | `wmo-im/iwxxm-translation` | informative | creation sources (fixtures) | README: no official WMO/ICAO status |
| **AHL / exchange** | community.wmo.int AHL page; WMO-386 tables rescued there | normative-exchange | `RULE_SOURCE_URLS.md`, bulletin notes | TAC vs IWXXM `T1T2` |
| **Manual on Codes** | WMO-No. 306 Vol I.1 / I.3 | normative | mining notes + creation/validation | PDF → extract-pdf-to-repo; captcha common |
| **ICAO Annex 3 / Docs** | Annex 3, Doc 8896, 10003, 9766 | normative | `validation/ANNEX3_TAC_VALIDATION_SOURCES.md` | **Paywall** — landings + section cites only |
| **National US** | FMH-1, `iwxxm-us`, codes.nws.noaa.gov | normative (national) / normative-schema | `RULE_SOURCE_URLS.md` (profile=`iwxxm_us`) | Separate from annex3 profile |
| **Historical GIFTs** | old fork / `packages/gifts` | historical-GIFTs | gap columns only | ADR-014 — never ongoing SoT |
| **Community blogs / random mirrors** | third-party PDFs | informative or reject | — | Do not treat as normative |

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
