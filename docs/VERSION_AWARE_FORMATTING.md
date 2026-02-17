# Version-Aware Formatting Architecture

## Overview

This document describes the version-aware formatting rules implemented to ensure IWXXM compliance across different versions. The system automatically applies version-specific precision and formatting rules when generating IWXXM XML documents.

## Coordinate Precision Rules

Coordinate precision varies between supported IWXXM versions to balance accuracy with system requirements.

### Precision by Version

| Version | Decimals | Precision | Rationale |
|---------|----------|-----------|-----------|
| 2023-1 | 6 | ~0.111 meters per degree | High precision for modern systems |
| 2025-2 | 8 | ~1.1 millimeters per degree | ICAO Annex 3 high-precision standard |

### Coordinate Formatting Example

For coordinates (61.176667°N, -45.425°W):

- **2023-1**: `61.176667 -45.425000` (6 decimals)
- **2025-2**: `61.17666700 -45.42500000` (8 decimals)

### Implementation

```python
from src.config.version_formatting import format_coordinates

lat = 61.176667
lon = -45.425

for version in ["2023-1", "2025-2"]:
    formatted = format_coordinates(lat, lon, version)
    print(f"{version}: {formatted}")
```

## Elevation Formatting Rules

Elevation values are rounded to integer meters for all supported IWXXM versions.

### Rounding Rules by Version

| Version | Round To | Data Type | Rationale |
|---------|----------|-----------|-----------|
| 2023-1 | 0 (integer) | Integer | Meters provide sufficient precision |
| 2025-2 | 0 (integer) | Integer | Full-precision elevation data in meters |

### Elevation Formatting Example

For elevation 1234.567 meters:

- **2023-1**: `1235` (rounded to nearest integer)
- **2025-2**: `1235` (rounded to nearest integer)

### Implementation

```python
from src.config.version_formatting import format_elevation

elevation_m = 1234.567

for version in ["2023-1", "2025-2"]:
    formatted = format_elevation(elevation_m, version)
    print(f"{version}: {formatted}")
```

## Airport Name Formatting

All supported IWXXM versions (2023-1 and later) use full airport names.

### Format by Version

| Version | Format | Example |
|---------|--------|---------|
| 2023-1 | Long (official name) | `NARSARSUAQ INTERNATIONAL AIRPORT` |
| 2025-2 | Long (official name) | `NARSARSUAQ INTERNATIONAL AIRPORT` |

**Note**: Pre-2023 versions used short ICAO codes (e.g., `BGBW`) but are no longer supported.

## Vertical Datum Support

Different versions support different sets of vertical datum codes.

### IWXXM-Native Datums

- `EGM_96` - WGS84 ellipsoidal height (global standard)
- `NAVD88` - North American Vertical Datum (US/Canada)
- `AHD` - Australian Height Datum (Australia/territories)

### Custom Datums

Custom or region-specific datums are wrapped with `OTHER:` prefix:
- `OTHER:CGVD2013` - Canadian Geodetic Vertical Datum 2013
- `OTHER:EVRS2007` - European Vertical Reference System 2007

## Integration with ElevationService

The `ElevationService` now supports version-aware formatting through an optional `version` parameter:

```python
from src.utilities.elevation_service import ElevationService

service = ElevationService()

# Version-aware elevation retrieval
elevation_m, datum = service.get_elevation_data(
    icao="BGBW",
    default_elevation_ft=124,
    country_code="GL",
    version="2025-2"  # Apply 2025-2 formatting rules
)

# Backward compatible - uses default version if not specified
elevation_m, datum = service.get_elevation_data(
    icao="BGBW",
    default_elevation_ft=124
)
```

## Conversion Flow

When converting METAR to IWXXM, the formatting rules are applied in this order:

```
1. Extract raw data (unformatted)
2. Determine target IWXXM version
3. Apply version-specific formatting:
   - Coordinate precision
   - Elevation rounding
   - Name format
   - Datum representation
4. Generate XML with formatted data
```

## Migration Path: 2023-1 to 2025-2

### What Changes

1. **Coordinate Precision**: 6 decimals → 8 decimals (millimeter-level precision)
2. **Elevation**: Integer rounding unchanged (both use integer meters)
3. **Airport Names**: No change (both use full official names)
4. **Vertical Datums**: No change to supported datums

### Required Actions

- Update coordinate formatting to 8 decimals
- Ensure elevation data maintains full precision in meters
- Verify vertical datum mappings are current

### Code Update Example

```python
# 2023-1 format
lat_str = f"{lat:.6f}"

# 2025-2 format
lat_str = f"{lat:.8f}"

# Recommended: Use formatter for version-agnostic code
from src.config.version_formatting import format_coordinates
lat_str = format_coordinates(lat, lon, version="2025-2")
```

## Quality Assurance

### Validation Steps

1. **Precision Validation**: Verify decimal places match version requirements
2. **Rounding Validation**: Confirm elevation rounding applied correctly
3. **Format Validation**: Check XML output format matches IWXXM spec
4. **Roundtrip Testing**: Ensure data integrity through format conversions

### Test Coverage

Version formatting is validated through:
- Unit tests in `tests/test_elevation_version_formatting.py`
- Integration tests in `tests/test_version_switching.py`
- Roundtrip validation tests in `tests/test_roundtrip.py`

## Future Enhancements

### Planned

- [ ] Automated version detection from input METAR
- [ ] Version override capabilities at API level
- [ ] Format validation against IWXXM schema
- [ ] Performance optimization for bulk conversions

### Dependencies

- IWXXM schema definitions (currently stored in `schemas/iwxxm/`)
- Version metadata (`src/config/version_metadata.py`)
- Elevation data sources (`src/data/vertical_datum_map.json`)

## References

- ICAO Annex 3: Meteorological Service for International Air Navigation
- IWXXM Standard Specification: https://www.wmo.int/pages/prog/wis/2010/metadata/version_2_0/iwxxm/
- WGS 84 Technical Specification: https://www.nga.mil/ProductsandServices/Standards/WGS84/
