# IWXXM Comprehensive Validation Architecture

## Overview

The METAR-to-IWXXM backend implements a **7-layer comprehensive validation system** that validates IWXXM XML documents against multiple official WMO sources including XSD schemas, Schematron business rules, and RDF code lists.

**Status**: ✅ Fully Implemented (Phase 2 Complete)

> **Domain rule provenance (SoT):** This file is **engine / API wiring**, not the authority for
> *what* must pass. Prefer:
>
> | Concern | Standing doc |
> |---------|--------------|
> | E2E TAC → IWXXM pipeline | [../README.md](../README.md) §End-to-end strategy |
> | TAC / Annex 3 lint | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
> | Encode / nilReason | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
> | XSD + Schematron + RDF | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) §Validation strategy |
> | Product × gate matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) G1–G7 |
>
> **Release gate (domain):** produced IWXXM must pass **both XSD and Schematron** for the
> vendored pin (`vendor/schemas/iwxxm/…`, currently **2025-2**). OPMET Exchange Guidelines
> require Schematron on translator outputs — treat SCH as **blocking for release** even if
> older engine notes label layer 5 “non-blocking”. Paths below that still say `schemas/iwxxm/`
> are historical; runtime CI uses **`vendor/schemas/iwxxm`**.

### Engine layers ↔ domain stages

| Engine layer | Domain stage | Blocking for release? |
|--------------|--------------|----------------------|
| 1 AIRPORT_ICAO | Pre-condition (station metadata) | Project policy |
| 2 TAC_SYNTAX | Stage 1 TAC lint (`tac-validate`) | Yes for convert path |
| 3 XML_WELLFORMED | Stage 3 | Yes |
| 4 XML_SCHEMA | Stage 4 XSD | **Yes** |
| 5 SCHEMATRON | Stage 5 | **Yes for release** (domain) |
| 6 GML_REFERENCES | Advisory beyond SCH | Optional |
| 7 WMO_CODELISTS | Mostly inside SCH RDF; live optional | Prefer offline RDF |

**Product TAC checklists (before layers 3–5):** [../TAC_VALIDATION.md](../TAC_VALIDATION.md)
(A3-2 · A5-1 · A6 · A2-1/A2-2 · US RMK). Encode recipes:
[../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md).

---

## Validation Layers

The system implements all 7 validation layers defined in the IWXXM specification:

| Layer | Name | Type | Description | Source |
|-------|------|------|-------------|--------|
| 1 | AIRPORT_ICAO | Blocking | Validates ICAO airport code against database | Internal database |
| 2 | TAC_SYNTAX | Blocking | Validates TAC/METAR syntax basics | Internal rules → prefer [TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| 3 | XML_WELLFORMED | Blocking | Checks XML is well-formed | lxml parser |
| 4 | XML_SCHEMA | Blocking | Validates against official IWXXM XSD schemas | `vendor/schemas/iwxxm/<pin>/IWXXM/*.xsd` |
| 5 | SCHEMATRON | Blocking for release\* | Official Schematron (+ RDF `document()`) | `vendor/schemas/iwxxm/<pin>/IWXXM/rule/iwxxm.sch` |
| 6 | GML_REFERENCES | Non-blocking | Validates GML internal references | Internal logic |
| 7 | WMO_CODELISTS | Non-blocking / SCH-overlap | Offline RDF / optional live codes.wmo.int | `…/rule/*.rdf` |

\*Domain SoT / OPMET Guidelines: fail release if SCH does not run successfully. Engine may still
return soft failures during transitional `xslt2` skip — do not treat skip warnings as a pass.

### Execution Model

- **Blocking Layers (1-4):** Run sequentially. If any fails, validation stops immediately (configurable)
- **Layer 5 (Schematron):** Required for domain release gate; run after XSD against the **same** year line
- **Advisory Layers (6-7):** May run in parallel; collect all results even if some fail

---

## Architecture Components

Layers 3–7 (XML well-formed through WMO codelists) delegate to **`packages/iwxxm-validate`**
via the backend adapter **`apps/backend/src/services/iwxxm_validation_adapter.py`**. The
orchestrator no longer calls legacy `utilities/{xsd,schematron,gml}_validator` modules.

```
validation_orchestrator (layers 3–7)
        │
        ▼
iwxxm_validation_adapter  ──►  validate_iwxxm()  (packages/iwxxm-validate)
        │                              ├── wellformed (lxml)
        │                              ├── xsd
        │                              ├── schematron
        │                              ├── gml
        │                              └── codelists

POST /api/v1/validate  ──►  validate_iwxxm()  (F11 SDK wire unchanged)
```

Layer result dataclasses (`XSDValidationResult`, `SchematronValidationResult`,
`GMLValidationResult`, `CodelistValidationResult`) live in
`apps/backend/src/schemas/validation.py`.

### 1. Version Detection (`version_detector.py`)

Detects available IWXXM versions from git submodule tags and identifies upgrade opportunities.

**Key Features**:
- Scans `schemas/iwxxm/` git tags for available versions
- Reads `LATEST_VERSION` file for current WMO release
- Compares against configured versions in `iwxxm_versions.py`
- Generates upgrade reports

**Usage**:
```python
from utilities.version_detector import VersionDetector

detector = VersionDetector()
versions = detector.detect_versions()
report = detector.generate_version_report()
print(report)
```

**CLI**:
```bash
python -m backend --check-versions
```

### 2. IWXXM validation package (`packages/iwxxm-validate`)

Single entrypoint for XSD, Schematron, GML reference, and offline WMO codelist checks.

**Key modules**:
- `validate_iwxxm.py` — layered `validate_iwxxm(..., levels=...)`
- `xsd.py`, `schematron.py`, `gml.py`, `codelists.py` — layer implementations
- `ca_eccc_validate.py` — CA_ECCC layered reports (`stages` preserved)

**Usage (backend adapter)**:
```python
from src.services.iwxxm_validation_adapter import (
    validate_xml_schema,
    validate_schematron,
    validate_gml_references,
    validate_wmo_codelists,
)

xsd_result = validate_xml_schema(xml_content, version="2025-2")
sch_result = validate_schematron(xml_content, version="2025-2")
gml_ok, gml_issues = validate_gml_references(xml_content, version="2025-2")
```

**Schema sources** (runtime):
- `vendor/schemas/iwxxm/<pin>/IWXXM/*.xsd`
- `vendor/schemas/iwxxm/<pin>/IWXXM/rule/iwxxm.sch`
- `vendor/schemas/iwxxm/<pin>/IWXXM/rule/*.rdf`

### 3. Legacy backend validators (removed)

`utilities/xsd_validator.py`, `utilities/schematron_validator.py`, and
`utilities/gml_validator.py` were removed in EV-037 TD-1. Do not reintroduce duplicate
IWXXM layer logic in `apps/backend` — extend `packages/iwxxm-validate` instead.

### 4. Code List Parser (`codelist_parser.py`) — TAC / RDF utilities

Validates code list references against official WMO RDF codelists.

**Key Features**:
- Parses RDF/XML codelist files using SKOS vocabulary
- Per-version codelist caching
- Extracts xlink:href references from XML
- Validates code values against allowed lists

**Usage**:
```python
from utilities.codelist_parser import get_codelist_parser
from utilities.schema_registry import get_schema_registry

registry = get_schema_registry()
codelists_dir = registry.get_codelists_dir("2025-2")
parser = get_codelist_parser("2025-2", codelists_dir)

result = parser.validate_xml_codelists(xml_content)
```

**Codelist Sources**:
- `schemas/iwxxm/IWXXM/rule/codes.wmo.int-49-2-AerodromeRecentWeather.rdf`
- `schemas/iwxxm/IWXXM/rule/codes.wmo.int-49-2-CloudAmountReportedAtAerodrome.rdf`
- `schemas/iwxxm/IWXXM/rule/codes.wmo.int-common-nil.rdf`
- 20+ additional RDF files

### 5. Validation Orchestrator (`validation_orchestrator.py`)

Coordinates all 7 validation layers with proper sequencing and error handling.

**Key Features**:
- Sequential execution of blocking layers (1-4)
- Parallel execution of non-blocking layers (5-7) using ThreadPoolExecutor
- Configurable stop-on-error behavior
- Comprehensive result aggregation
- Layer-specific issue tracking

**Usage**:
```python
from services.validation_orchestrator import get_validation_orchestrator

orchestrator = get_validation_orchestrator()

result = orchestrator.validate_complete(
    tac_text="METAR KJFK 112051Z 18012KT 10SM FEW250 15/07 A3005",
    xml_content=iwxxm_xml,
    version="2025-2",
    layers=None,  # All layers
    stop_on_error=True
)

print(f"Valid: {result.is_valid}")
print(f"Layers passed: {len(result.layers_passed)}/{len(result.layers_run)}")
print(f"Total issues: {len(result.all_issues)}")

# Issues by layer
for layer, issues in result.issues_by_layer.items():
    print(f"\n{layer.name}: {len(issues)} issues")
    for issue in issues:
        print(f"  - {issue.message}")
```

---

## API Endpoints

### POST /api/v1/validate

Comprehensive 7-layer validation endpoint.

**Request**:
```bash
curl -X POST http://localhost:8001/api/v1/validate \
  -H "Authorization: Bearer $TOKEN" \
  -F "manual_text=METAR KJFK 112051Z 18012KT 10SM FEW250 15/07 A3005" \
  -F "iwxxm_version=2025-2" \
  -F "layers=ALL" \
  -F "stop_on_error=true"
```

**Response**:
```json
{
  "is_valid": true,
  "version": "2025-2",
  "layers_run": ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_WELLFORMED", "XML_SCHEMA", "SCHEMATRON", "GML_REFERENCES", "WMO_CODELISTS"],
  "layers_passed": ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_WELLFORMED", "XML_SCHEMA", "SCHEMATRON", "GML_REFERENCES", "WMO_CODELISTS"],
  "layers_failed": [],
  "total_issues": 0,
  "issues": [],
  "issues_by_layer": {},
  "stopped_at_layer": null
}
```

**Parameters**:
- `manual_text` (required): METAR TAC text to validate
- `xml_content` (optional): Pre-converted XML (if omitted, TAC will be converted)
- `iwxxm_version` (default: "2025-2"): Target IWXXM version
- `layers` (default: ["ALL"]): Validation layers to run
  - "ALL": Run all 7 layers
  - Or specify: ["AIRPORT_ICAO", "TAC_SYNTAX", "XML_SCHEMA", "SCHEMATRON", ...]
- `stop_on_error` (default: true): Stop at first blocking layer failure

### POST /api/v1/convert

Conversion endpoint now includes validation results in metadata.

**Request**:
```bash
curl -X POST http://localhost:8001/api/v1/convert \
  -H "Authorization: Bearer $TOKEN" \
  -F "manual_text=METAR KJFK 112051Z 18012KT 10SM FEW250 15/07 A3005" \
  -F "iwxxm_version=2025-2"
```

**Response**: Includes converted XML plus validation metadata (layers 1-2 by default)

---

## Version Upgrade Workflow

1. **Check for New Versions**:
   ```bash
   cd backend
   python -m src --check-versions
   ```

2. **Update Git Submodule**:
   ```bash
   cd schemas/iwxxm
   git fetch --tags
   git checkout v2026-1  # New version
   cd ../..
   ```

3. **Configure New Version**:
   Edit `backend/src/config/iwxxm_versions.py`:
   ```python
   SUPPORTED_VERSIONS = {
       "2026-1": {
           "name": "IWXXM 2026-1",
           "namespace_uri": "http://icao.int/iwxxm/2026-1",
           "schema_url": "http://schemas.wmo.int/iwxxm/2026-1/iwxxm.xsd",
           "xsd_file": "iwxxm.xsd",
           "schematron_file": "rule/iwxxm.sch",
           "codelists_dir": "rule",
           "status": "latest",
           "release_date": "2026-11-25",
           "wmo_amendment": 85
       },
       # ... existing versions
   }
   ```

4. **Test new version**:
   ```bash
   uv run pytest packages/iwxxm-validate/tests -k "2026-1" -v
   uv run pytest apps/backend/tests/validation -k "orchestrator" -v
   ```

5. **Update Default Version** (if needed):
   ```python
   DEFAULT_VERSION = "2026-1"
   ```

---

## Testing

### Run validation tests

```bash
# Package layer tests (XSD, Schematron, GML, codelists)
uv run pytest packages/iwxxm-validate/tests -v

# Backend orchestrator + adapter
uv run pytest apps/backend/tests/unit/test_validation_orchestrator_unit.py -v
uv run pytest apps/backend/tests/validation/test_validation_orchestrator.py -v

# Full backend unit suite
make test-unit
```

### Integration Tests

```bash
# Requires schemas/iwxxm/ submodule initialized
pytest tests/ -m integration -v

# Slow tests (full pipeline)
pytest tests/ -m slow -v
```

### Test coverage (post TD-1)

- `packages/iwxxm-validate`: XSD, Schematron, GML, codelists, CA bundle
- `iwxxm_validation_adapter.py`: backend ↔ package mapping
- `validation_orchestrator.py`: layer sequencing and aggregation
- `codelist_parser.py`: RDF parse helpers (layer 7 overlap with package)

---

## Performance Considerations

### Caching

Layer caching is owned by **`packages/iwxxm-validate`** (compiled XSD/Schematron, RDF
codelist indexes). The backend adapter is stateless.

### Parallel Execution

Layers 5-7 (Schematron, GML, Codelists) run in parallel:
- Uses `ThreadPoolExecutor` with max 3 workers
- 30-second timeout per validator
- Errors in one validator don't block others

### Working directories

Schematron RDF `document()` resolution is handled inside **`packages/iwxxm-validate`**
(offline bundled RDF under `vendor/schemas/iwxxm/.../rule/`).

---

## Dependencies

### Required Python Packages

```toml
[tool.poetry.dependencies]
lxml = ">=4.9.0"  # XML parsing, XSD validation, Schematron
```

### Required Git Submodules

```bash
# Initialize submodules
git submodule update --init --recursive

# Submodules:
# - schemas/iwxxm/ (WMO IWXXM schemas)
# - schemas/iwxxm-codelists/ (WMO RDF code lists) 
# - schemas/iwxxm-modelling/ (UML/EA generators only — runtime SCH is vendor/schemas/iwxxm/.../iwxxm.sch)
```

---

## Troubleshooting

### Issue: XSD validation fails with "Schema not found"

**Solution**: Ensure git submodule is initialized:
```bash
cd schemas/iwxxm
git submodule update --init
ls IWXXM/iwxxm.xsd  # Should exist
```

### Issue: Schematron validation fails with "RDF file not found"

**Solution**: Check RDF files exist in codelists directory:
```bash
ls schemas/iwxxm/IWXXM/rule/*.rdf
```

Schematron creates working directory with copies of these files.

### Issue: Validation very slow on first run

**Expected**: First validation compiles schemas/Schematron rules and parses RDF files.
Subsequent validations use cached compiled objects.

Clear cache to free memory:
```python
validator.clear_cache()
```

### Issue: "document() function not found" in Schematron

**Solution**: Schematron validator automatically sets up working directory with RDF files.
Ensure `get_codelists_dir()` returns valid path with `.rdf` files.

---

## Future Enhancements

1. **Async Validation**: Convert orchestrator to use `asyncio` for better concurrency
2. **Validation Profiles**: Pre-configured layer combinations for different use cases
3. **Custom Schematron Rules**: Support for organization-specific business rules
4. **Validation Reports**: HTML/PDF report generation for validation results
5. **Performance Metrics**: Track validation times per layer for monitoring

---

## References

- **WMO IWXXM Repository**: https://github.com/wmo-im/iwxxm
- **IWXXM Schemas**: https://schemas.wmo.int/iwxxm/
- **WMO Code Registry**: https://codes.wmo.int/
- **lxml Documentation**: https://lxml.de/
- **ISO Schematron**: http://www.schematron.com/

---

**Last Updated**: 2026-08-26  
**Implementation Version**: EV-037 TD-1 (validation stack consolidation)  
**Status**: ✅ Production Ready — layers 3–7 in `packages/iwxxm-validate`
