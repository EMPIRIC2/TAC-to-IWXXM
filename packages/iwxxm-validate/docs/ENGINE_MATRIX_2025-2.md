# Engine matrix — IWXXM 2025-2 Schematron + XSD (EV-055 / #980 / #979)

[Corpus: product §F2] [Corpus: product §F13] [Corpus: decisions §EV-055]

| Layer      | Engine                                                 | 2025-2 behavior                                                                                          | Soft codes                                   |
| ---------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| XSD        | **lxml** `validate()` / `xsd.py`                       | Compile fails on GML `AbstractFeature` substitutionGroup for `{http://icao.int/iwxxm/2025-2}BasicReport` | `SCHEMA_IMPORT_WARNING` (strict XSD skipped) |
| XSD        | **native** `validate_iwxxm` (xmloxide + catalog roots) | Schema compiles and validates                                                                            | none for this gap                            |
| Schematron | **lxml** `schematron.py`                               | `queryBinding="xslt2"` unsupported                                                                       | `SCHEMATRON_SKIPPED`                         |
| Schematron | **native** `validate_iwxxm`                            | Evaluates Schematron                                                                                     | does **not** emit `SCHEMATRON_SKIPPED`       |

## Disposition (hard this cycle)

- **#980 / #979**: Enable/fix via **native** path (`D-S064-sch-hard=1`, `D-S064-xsd-hard=1`).
- Quality metrics / corpus precompute must call `validate_for_quality_metrics` → `validate_iwxxm`.
- lxml soft-skips remain documented fallback when `_rust` is not built — not an acceptable
  Quality metrics close when native is available.

## Root cause (#979)

- **File**: vendored `vendor/schemas/iwxxm/2025-2` IWXXM XSD (BasicReport element).
- **Import / QName**: `{http://www.opengis.net/gml/3.2}AbstractFeature` substitutionGroup
  does not resolve under lxml's XMLSchema compile for this pin.
- **Fix**: use native catalog-rooted validation (no vendor hand-edit).

## Backend parity

- Public `/api/v1/validate` already calls `validate_iwxxm`.
- `ValidationOrchestrator` Layer 4 (XSD) and Layer 5 (Schematron) prefer native when
  `rust_available()`; otherwise fall back to legacy lxml utilities (soft-skip codes).
