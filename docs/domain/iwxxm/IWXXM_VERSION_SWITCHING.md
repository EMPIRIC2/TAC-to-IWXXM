# IWXXM Version Switching Implementation

## Overview

This document describes the implementation of dynamic IWXXM version switching in the metar-to-IWXXM system. The system supports two IWXXM versions (2025-2 and 2023-1) with automatic conversion and migration between versions.

## Supported Versions

| Version | Status | Release Date | WMO Amendment | Breaking Changes from Prior |
|---------|--------|--------------|---------------|-----|
| 2025-2 | Latest | 2025-11-25 | 82 | Removed runway state elements, removed measures.xsd |
| 2023-1 | Previous | 2023-06-02 | 78 | None |

**Deprecated Versions**: 2021-2, 2018, 2016, and all 3.x versions are no longer supported as of 2026-02-13.

**Note**: Version 2025-1 does not exist in WMO repositories. Requests for 2025-1 are automatically remapped to 2025-2.

## Architecture

### 1. Version Configuration System

**File**: [backend/src/config/iwxxm_versions.py](../backend/src/config/iwxxm_versions.py)

This module provides:
- `SUPPORTED_VERSIONS`: Dictionary mapping version strings to configuration
- `DEFAULT_VERSION`: Default version (2025-2)
- Configuration includes:
  - Namespace URIs (`http://icao.int/iwxxm/{VERSION}`)
  - Schema URLs
  - Feature flags (has_measures_xsd, split_nil_codelists)
  - Breaking changes per version
  - Local schema paths

**Key Functions**:
- `normalize_version(version)`: Handles version remapping and defaults
- `get_version_config(version)`: Retrieves full configuration
- `get_namespace_uri(version)`: Gets XML namespace
- `get_schema_url(version)`: Gets remote schema location
- `get_breaking_changes(from_version, to_version)`: Lists breaking changes

### 2. Schema Registry

**File**: [backend/src/utilities/schema_registry.py](../backend/src/utilities/schema_registry.py)

Centralized registry for schema file resolution:
- Caches schema file paths per version
- Resolves XSD, Schematron, and codelist files
- Ensures submodules are properly initialized
- Provides singleton pattern for global access

**Key Class**: `SchemaRegistry`
- `get_xsd_path(version)`: Returns path to XSD schema
- `get_schematron_path(version)`: Returns path to Schematron rules
- `get_codelists_dir(version)`: Returns path to code list directory
- `list_codelists(version)`: Lists available code lists

### 3. GIFTs Version Adapter

**File**: [backend/src/utilities/gifts_adapter.py](../backend/src/utilities/gifts_adapter.py)

Wraps GIFTs library (metarDecoder, metarEncoder) with version support:
- Accepts version parameter in constructor
- Sets IWXXM version dynamically before encoding
- Caches encoder instances per version
- Singleton decoder instance

**Key Classes**:
- `GIFTsEncoder`: Version-aware METAR encoder
- `GIFTsDecoder`: TAC decoder (version-agnostic, but accepts parameter for consistency)
- `get_encoder(version)`: Get cached encoder
- `get_decoder()`: Get decoder
- `convert_tac_to_iwxxm(tac_text, version)`: Convenience function

**GIFTs Patches**:
1. **xmlConfig.py**: Added `set_iwxxm_version(version)` function to dynamically change namespace URIs
2. **Common.py**: Updated `Base.__init__()` to accept optional `version` parameter
3. **metarEncoder.py**: Updated `Annex3.__init__()` to accept optional `version` parameter

### 4. Version Migration

**File**: [backend/src/utilities/version_migration.py](../backend/src/utilities/version_migration.py)

Handles XML transformation when converting between versions:
- Detects breaking changes from breaking_changes configuration
- Automatically removes/transforms elements as needed
- Logs warnings for each breaking change

**Key Function**: `migrate_xml(xml_content, from_version, to_version)`

**Breaking Changes Handled**:
- **2023-1 → 2025-2**: Removes `iwxxm:runwayState` and `iwxxm:AerodromeRunwayState` elements
- Runway state information is no longer part of METAR in 2025-2

### 5. Code List Management

**File**: [backend/src/utilities/codelist_parser.py](../backend/src/utilities/codelist_parser.py)

Parses RDF/XML code lists from WMO repositories:
- Loads code list files on-demand per version
- Validates element values against allowed codes
- Caches parsed code lists in memory

**Key Classes**:
- `CodeListParser`: Parses individual RDF files
- `CodeListRegistry`: Manages parsers per version
- Version-specific code list validation

### 6. Conversion Pipeline Updates

**File**: [backend/src/utilities/conversion.py](../backend/src/utilities/conversion.py)

Updated conversion functions to accept version parameter:
- `convert_metar_tac(tac_text, iwxxm_version=None)`: Version-aware conversion
- `convert_metar_tac_with_metadata(tac_text, iwxxm_version=None)`: Includes aerodrome enrichment

**Defaults to 2025-2** if version not specified.

### 7. API Endpoints

**File**: [backend/src/api.py](../backend/src/api.py)

#### POST /api/v1/convert

**Version Parameter**:
- `iwxxm_version` (form parameter, default: "2025-2")
  - Options: "2025-2" (latest), "2023-1" (previous), "2025-1" (remaps to 2025-2)
  - Deprecated versions (2021-2, 2018, 2016, 3.x) will return HTTP 400 error
  - Validated automatically

**Example Request**:
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "manual_text=METAR KJFK 231751Z..." \
  -F "iwxxm_version=2025-2" \
  http://localhost:8000/api/v1/convert
```

#### GET /api/v1/versions

**New Endpoint** - Lists all supported versions with metadata

**Response**:
```json
{
  "default_version": "2025-2",
  "supported_versions": [
    {
      "version": "2025-2",
      "name": "IWXXM 2025-2",
      "status": "latest",
      "release_date": "2025-11-25",
      "wmo_amendment": 82
    },
    ...
  ],
  "notes": {
    "2025-1": "Version 2025-1 does not exist; requests are auto-remapped to 2025-2"
  }
}
```

## Data Flow

### METAR to IWXXM Conversion with Version Support

```
TAC Input
    ↓
API Endpoint (/api/v1/convert)
    ├─ Normalize version (2025-1 → 2025-2)
    ├─ Validate version (error if unsupported)
    ↓
Conversion Pipeline (conversion.py)
    ├─ TAC Validation (Layer 1-2)
    ├─ GIFTs Adapter
    │   ├─ Decoder: metarDecoder.Annex3()
    │   ├─ Encoder: metarEncoder.Annex3(version)
    │   └─ Namespace set matching version
    ↓
IWXXM XML Output
    ├─ Namespace: http://icao.int/iwxxm/{VERSION}
    ├─ Schema location: https://schemas.wmo.int/iwxxm/{VERSION}/iwxxm.xsd
    └─ Element structure per version
```

### Version Migration (if needed)

```
Source IWXXM XML (e.g., 2023-1)
    ↓
Migrate (version_migration.py)
    ├─ Parse XML
    ├─ Detect breaking changes
    ├─ Remove/transform elements
    ├─ Log warnings
    ↓
Target IWXXM XML (e.g., 2025-2)
```

## File Structure

```
project_root/
├── schemas/
│   ├── VERSION_MANIFEST.json           # Version metadata
│   ├── iwxxm/                          # IWXXM schemas (Git submodule)
│   │   └── IWXXM/
│   │       ├── iwxxm.xsd
│   │       ├── rule/
│   │       │   ├── iwxxm.sch           # Schematron rules
│   │       │   └── *.rdf               # Code lists
│   ├── iwxxm-codelists/                # Code lists (Git submodule)
│   └── iwxxm-modelling/                # Schematron sources (Git submodule)
├── GIFTs/                              # METAR encoder/decoder
│   └── gifts/
│       ├── common/
│       │   ├── xmlConfig.py            # PATCHED: version support
│       │   ├── Common.py               # PATCHED: version parameter
│       ├── metarEncoder.py             # PATCHED: version parameter
│       └── metarDecoder.py
└── backend/
    └── src/
        ├── config/
        │   └── iwxxm_versions.py       # Version configuration
        ├── utilities/
        │   ├── schema_registry.py       # NEW: Schema file resolution
        │   ├── gifts_adapter.py         # NEW: Version-aware GIFTs wrapper
        │   ├── version_migration.py     # NEW: XML migration
        │   ├── codelist_parser.py       # NEW: Code list validation
        │   └── conversion.py            # UPDATED: Version parameter
        └── api.py                       # UPDATED: Version endpoints
```

## Setup and Installation

### 1. Initialize Git Submodules

```bash
git submodule update --init --recursive schemas/iwxxm
git submodule update --init --recursive schemas/iwxxm-codelists
git submodule update --init --recursive schemas/iwxxm-modelling
```

### 2. Install Dependencies

The backend dependencies are already configured. If adding Schematron validation later:
```bash
# CRUX (Java-based Schematron validator) - manual installation
# https://github.com/dcarver1/crux
# Requires Java 11+
```

### 3. Verify Setup

Check version endpoint:
```bash
curl http://localhost:8000/api/v1/versions
```

## Version-Specific Features

### IWXXM 2025-2 Features
- `has_measures_xsd`: False (removed, consolidated to common.xsd)
- `split_nil_codelists`: True (separate common/nil and iwxxm/nil URI spaces)
- New packages: Quantitative Volcanic Ash, Volcano Observatory
- Breaking changes from 2023-1: Runway state removal

### IWXXM 2023-1 Features
- `has_measures_xsd`: True
- `split_nil_codelists`: False
- Stable, widely-used version
- Previous stable release before 2025-2

## Testing

### Version Switching Tests

Run version-specific tests:
```bash
cd backend
uv run pytest tests/test_version_switching.py -v
uv run pytest tests/test_version_migration.py -v
uv run pytest tests/test_schema_registry.py -v
```

### Integration Tests

Conversion with version parameter:
```python
from src.utilities.conversion import convert_metar_tac

# Convert to 2025-2 (default - latest)
xml_2025_2 = convert_metar_tac(metar_text)

# Convert to 2023-1 (previous stable)
xml_2023_1 = convert_metar_tac(metar_text, iwxxm_version="2023-1")
```

## Future Work

### Phase 2: Schematron Validation (Not Yet Implemented)

- [Planned] Integrate CRUX for version-specific Schematron validation
- [Planned] Add Schematron as Layer 5 validation in validation service
- [Planned] Version-aware code list validation from RDF files

### Performance Optimization

- Cache parsed Schematron files per version
- Consider async Schematron validation
- Pre-warm schema cache on startup

### Extended Version Support

- Consider adding older versions (2018-x, 2020-x) if needed
- Track version deprecation timelines
- Implement version sunset notifications

## Troubleshooting

### Submodules Not Initialized

**Error**: `FileNotFoundError: Schema file not found`

**Solution**:
```bash
cd /root/metar-to-IWXXM
git submodule update --init --recursive
```

### Version Not Supported

**Error**: `ValueError: IWXXM version 'X' is not supported` or `VersionDeprecatedError`

**Solution**: Use only supported versions: 2025-2 (latest) or 2023-1 (previous). Version 2025-1 auto-remaps to 2025-2. Pre-2023 versions (2021-2, 2018, 2016, 3.x) are deprecated and will be rejected.

### Namespace Mismatch

**Issue**: XML has 2023-1 namespace but schema expects 2025-2

**Solution**: Ensure API `iwxxm_version` parameter matches intended output version

## References

- [WMO IWXXM GitHub](https://github.com/wmo-im/iwxxm)
- [IWXXM Schemas](https://schemas.wmo.int/iwxxm)
- [GIFTs Library](https://github.com/mgoberfield/GIFTs)
- [Schematron Validation](https://github.com/wmo-im/iwxxm-modelling)
