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

### 2. XSD Schema Validator (`xsd_validator.py`)

Validates IWXXM XML against official WMO XSD schemas using lxml.

**Key Features**:
- Per-version schema compilation and caching
- Resolves XSD paths via `SchemaRegistry`
- Detailed error reporting with line/column numbers
- Singleton pattern for efficiency

**Usage**:
```python
from utilities.xsd_validator import validate_xml_schema

result = validate_xml_schema(xml_content, version="2025-2")

if not result.is_valid:
    for issue in result.issues:
        print(f"Line {issue.details['line']}: {issue.message}")
```

**Schema Sources**:
- `schemas/iwxxm/IWXXM/iwxxm.xsd` - Main IWXXM schema
- `schemas/iwxxm/IWXXM/metarSpeci.xsd` - METAR/SPECI specific
- `schemas/iwxxm/externalSchema/` - GML, OGC, ISO dependencies

### 3. Schematron Validator (`schematron_validator.py`)

Validates IWXXM XML against official WMO Schematron business rules using lxml.isoschematron.

**Key Features**:
- Pure Python implementation (no Java/CRUX dependency)
- Per-version Schematron compilation and caching
- Automatic RDF codelist file setup for `document()` function
- SVRL (Schematron Validation Report Language) parsing
- Working directory management for RDF dependencies

**Usage**:
```python
from utilities.schematron_validator import validate_schematron

result = validate_schematron(xml_content, version="2025-2")

if not result.is_valid:
    for issue in result.issues:
        print(f"{issue.details['pattern_id']}: {issue.message}")
```

**Schematron Sources**:
- `schemas/iwxxm/IWXXM/rule/iwxxm.sch` - 867 lines, 100+ business rules
- RDF codelists: `schemas/iwxxm/IWXXM/rule/*.rdf` (referenced via `document()`)

**Example Rules**:
- METAR_SPECI.MeteorologicalAerodromeObservationReport-7: Automated station must be flagged when clouds not detected
- METAR_SPECI.AerodromeRunwayVisualRange-1: RVR must be in metres
- METAR_SPECI.AerodromeSeaState-1: Sea state and wave height are mutually exclusive

### 4. GML Reference Validator (`gml_validator.py`)

Validates GML internal references (xlink:href="#id") against gml:id attributes.

**Key Features**:
- Builds ID registry from all `gml:id` attributes
- Validates all `xlink:href="#..."` internal references
- Detects duplicate `gml:id` values
- XPath-based error reporting

**Usage**:
```python
from utilities.gml_validator import validate_gml_references

result = validate_gml_references(xml_content)

if not result.is_valid:
    print(f"Found {result.broken_references} broken references")
    print(f"Total IDs: {result.total_ids}, Total refs: {result.total_references}")
```

### 5. Code List Validator (`codelist_parser.py`)

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

### 6. Validation Orchestrator (`validation_orchestrator.py`)

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

4. **Test New Version**:
   ```bash
   pytest tests/test_xsd_validator.py -k "2026-1"
   pytest tests/test_schematron_validator.py -k "2026-1"
   ```

5. **Update Default Version** (if needed):
   ```python
   DEFAULT_VERSION = "2026-1"
   ```

---

## Testing

### Run All Validation Tests

```bash
cd backend

# XSD validation tests
pytest tests/test_xsd_validator.py -v

# Schematron validation tests  
pytest tests/test_schematron_validator.py -v

# GML validation tests
pytest tests/test_gml_validator.py -v

# Codelist validation tests
pytest tests/test_codelist_validator.py -v

# Orchestrator tests
pytest tests/test_validation_orchestrator.py -v

# Version detection tests
pytest tests/test_version_detector.py -v

# All validation tests
pytest tests/test_*validator*.py tests/test_validation_orchestrator.py -v
```

### Integration Tests

```bash
# Requires schemas/iwxxm/ submodule initialized
pytest tests/ -m integration -v

# Slow tests (full pipeline)
pytest tests/ -m slow -v
```

### Test Coverage

Expected coverage from validation implementation:
- `version_detector.py`: 100%
- `xsd_validator.py`: 95%+
- `schematron_validator.py`: 95%+
- `gml_validator.py`: 98%+
- `codelist_parser.py` (XML validation): 92%+
- `validation_orchestrator.py`: 90%+

---

## Performance Considerations

### Caching

All validators implement caching for performance:

1. **XSD Validator**: Compiled schemas cached per version
2. **Schematron Validator**: Compiled Schematron cached per version
3. **Code List Parser**: Parsed RDF files cached per version
4. **Schema Registry**: File paths cached with LRU decorator

### Parallel Execution

Layers 5-7 (Schematron, GML, Codelists) run in parallel:
- Uses `ThreadPoolExecutor` with max 3 workers
- 30-second timeout per validator
- Errors in one validator don't block others

### Working Directories

Schematron validator creates temporary working directories:
- Copies RDF files for `document()` function
- Cleaned up on validator destruction or explicit `.clear_cache()`

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

**Last Updated**: 2026-02-11  
**Implementation Version**: Phase 2 Complete  
**Status**: ✅ Production Ready
