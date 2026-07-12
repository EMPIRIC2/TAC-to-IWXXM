# Integration Guide: Version-Aware Formatting

## Quick Start

### For Elevation Data

```python
from src.utilities.elevation_service import ElevationService

service = ElevationService()

# Get elevation with version-specific formatting
elevation_m, datum = service.get_elevation_data(
    icao="BGBW",
    default_elevation_ft=124,
    version="2025-2"  # Automatically applies precision rules
)

# The elevation will be rounded according to version rules:
# - 2016/2018: rounded to 1 decimal
# - 2021-2+: no rounding (full precision)
```

### For Coordinates

```python
from src.config.version_formatting import format_coordinates

lat, lon = 61.176667, -45.425

# Format for different versions
coords_2018 = format_coordinates(lat, lon, "2018")  # "61.18 -45.43"
coords_2025 = format_coordinates(lat, lon, "2025-2")  # "61.17666700 -45.42500000"
```

## Conversion Integration

### In METAR-to-IWXXM Conversion

When creating IWXXM documents, determine the target version early and apply formatting consistently:

```python
from src.utilities.elevation_service import ElevationService
from src.config.version_formatting import format_coordinates, format_elevation
from src.schemas.conversion import ConversionRequest

def convert_metar_to_iwxxm(metar_data: str, target_version: str = "2025-2"):
    """Convert METAR to IWXXM with version-aware formatting."""
    
    # Initialize services
    elevation_service = ElevationService()
    
    # Extract airport data
    icao = extract_icao(metar_data)
    coords = get_airport_coordinates(icao)
    elevation_ft = get_airport_elevation(icao)
    
    # Apply version-aware formatting
    lat_str = coords[0]
    lon_str = coords[1]
    formatted_coords = format_coordinates(
        float(coords[0]), 
        float(coords[1]), 
        version=target_version
    )
    
    elevation_m, datum = elevation_service.get_elevation_data(
        icao=icao,
        default_elevation_ft=elevation_ft,
        version=target_version
    )
    
    # Build IWXXM document with formatted data
    iwxxm_doc = build_iwxxm_document(
        icao=icao,
        coordinates=formatted_coords,
        elevation=elevation_m,
        datum=datum,
        version=target_version
    )
    
    return iwxxm_doc
```

## Version Detection

### Determining the Target Version

```python
from src.utilities.version_detector import detect_iwxxm_version

# Detect from existing IWXXM document
detected_version = detect_iwxxm_version(iwxxm_xml_string)

# Or explicitly specify
target_version = "2025-2"
```

## Precision Requirements by Use Case

### Aviation Safety Critical (2025-2)

Maximum precision for operational use:

```python
# Coordinates: 8 decimals (~1.1 mm precision)
# Elevation: Integer with full source precision
# Names: Full airport name

elevation_m, datum = elevation_service.get_elevation_data(
    icao=icao,
    default_elevation_ft=elevation_ft,
    version="2025-2"
)
```

### Standard Operations (2021-2)

Modern systems with good precision:

```python
# Coordinates: 6 decimals (~0.111 m precision)
# Elevation: Integer
# Names: Full airport name

elevation_m, datum = elevation_service.get_elevation_data(
    icao=icao,
    default_elevation_ft=elevation_ft,
    version="2021-2"
)
```

### Legacy Systems (2018)

Compatibility with older systems:

```python
# Coordinates: 2 decimals (~1.1 km precision)
# Elevation: 1 decimal place
# Names: Short ICAO code

elevation_m, datum = elevation_service.get_elevation_data(
    icao=icao,
    default_elevation_ft=elevation_ft,
    version="2018"
)
```

## Handling Vertical Datums

### Automatic Datum Selection

```python
service = ElevationService()

# Datum is automatically selected based on country
elevation_m, datum = service.get_elevation_data(
    icao="KJFK",
    default_elevation_ft=13,
    country_code="US",
    version="2025-2"
)
# Returns: elevation_m=4, datum="NAVD88" (US default)

elevation_m, datum = service.get_elevation_data(
    icao="LFPG",
    default_elevation_ft=271,
    country_code="FR",
    version="2025-2"
)
# Returns: elevation_m=83, datum="EGM_96" (global default)
```

### Custom Datum Mapping

```python
# Add custom elevation override with specific datum
service.add_airport_override(
    icao="CYQX",
    elevation_m=10,
    vertical_datum="OTHER:CGVD2013",
    source="Canadian geodetic data",
    notes="Canadian coordinates with CGVD2013 datum"
)

# Retrieve with custom datum
elevation_m, datum = service.get_elevation_data(
    icao="CYQX",
    version="2025-2"
)
# Returns: elevation_m=10, datum="OTHER:CGVD2013"
```

## Testing Version Formatting

### Unit Tests

```python
from src.config.version_formatting import format_elevation, format_coordinates

def test_version_formatting():
    """Test that formatting rules are correctly applied."""
    
    # Test elevation formatting
    value = 1234.567
    
    # 2016/2018: round to 1 decimal
    assert format_elevation(value, "2016") == round(value, 1)
    
    # 2021-2+: round to integer
    assert format_elevation(value, "2021-2") == round(value, 0)
    
    # Test coordinate formatting
    lat, lon = 61.176667, -45.425000
    
    # 2018: 2 decimals
    coords = format_coordinates(lat, lon, "2018")
    assert coords == "61.18 -45.43"
    
    # 2025-2: 8 decimals
    coords = format_coordinates(lat, lon, "2025-2")
    assert coords == "61.17666700 -45.42500000"
```

### Integration Tests

```python
def test_conversion_with_versions():
    """Test METAR conversion with different IWXXM versions."""
    metar = "METAR BGBW 121300Z 09008KT 9999 FEW060 SCT100 02/M02 A3012"
    
    # Convert to different versions
    for version in ["2016", "2018", "2021-2", "2023-1", "2025-2"]:
        iwxxm = convert_metar_to_iwxxm(metar, target_version=version)
        
        # Validate precision
        validate_coordinate_precision(iwxxm, version)
        validate_elevation_precision(iwxxm, version)
        validate_format(iwxxm, version)
```

## Performance Considerations

### Caching Formatted Values

For bulk conversions, cache formatted coordinates:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_formatted_coords(lat: float, lon: float, version: str) -> str:
    """Cache formatted coordinates to avoid repeated calculations."""
    return format_coordinates(lat, lon, version)

# Use in bulk conversion loop
for metar in metars:
    coords = get_formatted_coords(
        float(metar.latitude),
        float(metar.longitude),
        target_version
    )
```

### Batch Processing

```python
def batch_convert_metars(metars: List[str], version: str) -> List[str]:
    """Process multiple METARs with consistent version formatting."""
    
    elevation_service = ElevationService()
    results = []
    
    for metar in metars:
        iwxxm = convert_single_metar(
            metar,
            elevation_service=elevation_service,
            version=version
        )
        results.append(iwxxm)
    
    return results
```

## Troubleshooting

### Issue: Precision Mismatch

**Problem**: Formatted output doesn't match expected precision for version.

**Solution**: Verify version parameter is correctly passed:

```python
# Check version is applied
from src.config.version_formatting import get_coordinate_decimals

expected_decimals = get_coordinate_decimals("2025-2")  # Should be 8
print(f"Expected decimal places: {expected_decimals}")

# Verify formatting
coords = format_coordinates(61.176667, -45.425, "2025-2")
decimal_count = len(coords.split()[0].split('.')[-1])
assert decimal_count == expected_decimals
```

### Issue: Elevation Rounding Unexpected

**Problem**: Elevation rounded differently than expected.

**Solution**: Check the rounding rule for your version:

```python
from src.config.version_formatting import get_elevation_rounding, ELEVATION_FORMAT

version = "2025-2"
rounding = get_elevation_rounding(version)
rule = ELEVATION_FORMAT[version]

print(f"Version {version} elevation rules:")
print(f"  Round to: {rounding} decimal places")
print(f"  Rationale: {rule['rationale']}")
```

### Issue: Datum Not Recognized

**Problem**: Custom datum appears as `OTHER:DATUM` instead of expected code.

**Solution**: Check if datum needs to be added to mapping:

```python
# Add missing datum to service
service = ElevationService()
service.datum_map["datum_info"]["CGVD2013"] = {
    "iwxxm_code": "OTHER:CGVD2013",
    "description": "Canadian Geodetic Vertical Datum 2013",
    "region": "Canada"
}
service.save_datum_mapping()
```

## Best Practices

1. **Always specify version explicitly** - Don't rely on defaults for production
2. **Validate output against schema** - Ensure IWXXM compliance after formatting
3. **Test with boundary values** - Check precision at maximum/minimum coordinates
4. **Document version choices** - Make version selection criteria clear in code
5. **Use consistent version** - Apply same version across entire document
6. **Cache formatting rules** - Avoid repeated lookups in loops
