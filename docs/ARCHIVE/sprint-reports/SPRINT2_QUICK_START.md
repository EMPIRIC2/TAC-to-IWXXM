% Sprint 2 Quick Start Guide

# 🚀 Sprint 2: Dynamic Test Generation - Quick Start

## 60-Second Start

```bash
cd backend

# 1. Generate test data from live APIs
python3 scripts/generate_test_data.py

# 2. View coverage report
cat test-data/generated-tests/coverage_report.json

# 3. Run dynamic tests
pytest tests/test_dynamic_metar_generation.py -v
```

## What Gets Generated

**From AviationWeather.gov API**:
- 200+ real-world METARs from 7 world regions
- Live data updated every 3 hours
- Includes weather phenomena, clouds, visibility, temperature

**From OpenAIP + GIFTs**:
- Airport metadata enrichment (coordinates, elevation, country)
- Station names and ICAO codes
- Conflict detection across data sources

**Test Cases**:
- 200+ parameterized test cases
- Coverage tracking across:
  - ✅ 79+ unique stations
  - ✅ 7+ countries
  - ✅ 4+ world regions
  - ✅ 8+ weather phenomena types
  - ✅ 6+ cloud types
  - ✅ Simple/medium/complex complexity levels

## File Structure

```
backend/
├── src/
│   ├── clients/
│   │   ├── aviation_weather_client.py ← Live METAR API
│   │   ├── openaip_client.py ← Airport data
│   │   └── wmo_codelists_client.py ← Weather validation
│   ├── services/
│   │   └── airport_reconciliation.py ← Multi-source merger
│   └── testing/
│       └── metar_test_generator.py ← Test generator
├── tests/
│   └── test_dynamic_metar_generation.py ← Parameterized tests
├── scripts/
│   └── generate_test_data.py ← Standalone generation
└── test-data/
    └── generated-tests/
        ├── coverage_report.json
        ├── diverse_sample_200_3h.json
        └── regional_*.json
```

## Key APIs

### Generate Diverse Global Sample

```python
from src.testing.metar_test_generator import METARTestGenerator

generator = METARTestGenerator()

# Get 200 diverse METARs from all regions
test_cases = generator.diverse_sample(count=200, hours=3)
print(f"Generated {len(test_cases)} test cases")

# Show coverage
coverage = generator.get_coverage_report()
print(f"Stations: {len(coverage.unique_stations)}")
print(f"Phenomena: {sorted(coverage.weather_phenomena)}")
```

### Generate Region-Specific Tests

```python
# Get samples from specific region
europe_cases = generator.regional_sample("europe", count=50)

# Available regions:
# - north_america, europe, asia_pacific, south_america
# - africa, middle_east, australia
```

### Find Tests with Specific Weather

```python
# Get tests with rain, snow, or thunderstorms
weather_cases = generator.phenomenon_coverage(
    required_phenomena=['RA', 'SN', 'TS'],
    hours=6
)

for tc in weather_cases:
    print(f"{tc.station_id}: {tc.raw_metar}")
```

### Get Single Test Case

```python
tc = test_cases[0]

print(f"Station: {tc.station_id}")
print(f"METAR: {tc.raw_metar}")
print(f"Location: ({tc.latitude}, {tc.longitude})")
print(f"Country: {tc.country}")
print(f"Weather: {tc.weather_phenomena}")
print(f"Clouds: {tc.cloud_amounts}")
print(f"Complexity: {tc.complexity_score()}/10")
```

## Run Tests

### All Dynamic Tests (200+ parameterized)

```bash
pytest tests/test_dynamic_metar_generation.py -v
```

### Specific Test Class

```bash
# Test IWXXM 2025-2 conversion
pytest tests/test_dynamic_metar_generation.py::TestDynamicMETARConversion::test_convert_to_iwxxm_2025_2 -v

# Test regional coverage
pytest tests/test_dynamic_metar_generation.py::TestRegionalCoverage -v

# Test specific phenomena
pytest tests/test_dynamic_metar_generation.py::TestPhenomenonCoverage -v
```

### With Specific Region

```bash
pytest tests/test_dynamic_metar_generation.py::TestRegionalCoverage::test_regional_coverage_2025_2[europe] -v
```

### Generate Failure Report

```bash
# Run tests and see failures
pytest tests/test_dynamic_metar_generation.py -v --tb=short

# View failures for specific version
ls test-reports/dynamic-test-failures/2025-2/

# Analyze specific failure
cat test-reports/dynamic-test-failures/2025-2/KDCA_*.json | jq '.validation.errors[0:3]'
```

## Coverage Report Format

```json
{
  "total_cases": 87,
  "unique_stations": 79,
  "countries": ["CV", "KE", "MA", "MZ", ...],
  "regions": ["africa", "europe", "middle_east", ...],
  "weather_phenomena": ["BR", "DZ", "FG", "HZ", "RA", "SHRA", "SN", "TS"],
  "cloud_types": ["CB"],
  "cloud_amounts": ["BKN", "CLR", "FEW", "OVC", "SCT", "SKC"],
  "complexity_distribution": {
    "simple": 53,
    "medium": 28,
    "complex": 6
  }
}
```

## Common Tasks

### Regenerate Test Data (Fresh from API)

```bash
python3 scripts/generate_test_data.py
# Note: Uses live API, so different data each time (unless cached)

# Force bypass cache:
python3 scripts/generate_test_data.py --no-cache
```

### Test Specific Airport

```bash
# Look up a specific station
python3 << 'EOF'
from src.testing.metar_test_generator import METARTestGenerator

gen = METARTestGenerator()
cases = gen.diverse_sample(count=200)

# Find specific station
kdca_cases = [tc for tc in cases if tc.station_id == 'KDCA']
if kdca_cases:
    tc = kdca_cases[0]
    print(f"Found: {tc.raw_metar}")
    print(f"Location: ({tc.latitude}, {tc.longitude})")
    print(f"Weather: {tc.weather_phenomena}")
EOF
```

### Count Test Cases by Region

```python
from src.testing.metar_test_generator import METARTestGenerator

gen = METARTestGenerator()
cases = gen.diverse_sample(count=200)

# Count by region
by_region = {}
for tc in cases:
    region = tc.region or "unknown"
    by_region[region] = by_region.get(region, 0) + 1

print(by_region)
# Output: {'africa': 30, 'europe': 40, 'middle_east': 17, ...}
```

### Export Test Data to CSV

```python
import csv
from src.testing.metar_test_generator import METARTestGenerator

gen = METARTestGenerator()
cases = gen.diverse_sample(count=200)

# Export to CSV
with open("test_cases.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        'station_id', 'country', 'region', 'raw_metar', 
        'latitude', 'longitude', 'elevation',
        'weather_phenomena', 'cloud_amounts', 'complexity_score'
    ])
    writer.writeheader()
    
    for tc in cases:
        writer.writerow({
            'station_id': tc.station_id,
            'country': tc.country,
            'region': tc.region,
            'raw_metar': tc.raw_metar,
            'latitude': tc.latitude,
            'longitude': tc.longitude,
            'elevation': tc.elevation,
            'weather_phenomena': ','.join(tc.weather_phenomena),
            'cloud_amounts': ','.join(tc.cloud_amounts),
            'complexity_score': tc.complexity_score()
        })

print("Exported to test_cases.csv")
```

## Troubleshooting

### "No METARs found for region X"

**Cause**: API temporarily unavailable for that region

**Solution**:
```bash
# Try again (cached data helps)
python3 scripts/generate_test_data.py

# Check API is up
curl https://aviationweather.gov/api/data/metar?bbox=-10,35,40,70&hours=3&format=json
```

### "Could not find airport data"

**Cause**: OpenAIP data not in local cache

**Solution**: Either skip enrichment or download from OpenAIP API
```python
# Skip enrichment - test still works without airport data
# Just coordinates from API used

# Or download fresh data (requires OPENAIP_API_KEY)
from src.clients.openaip_client import download_openaip_data
import asyncio
asyncio.run(download_openaip_data(Path("data/open-aip")))
```

### "Caching issue - want fresh data"

**Solution**: Delete cache and regenerate
```bash
rm -rf backend/test-data/generated-tests/
python3 backend/scripts/generate_test_data.py
```

## Performance Tips

1. **First Run**: 30-60 seconds (API calls)
2. **Cached Runs**: <1 second (uses local JSON)
3. **Test Runs**: 1-5 minutes for 200+ tests

To speed up:
```bash
# Generate data once
python3 scripts/generate_test_data.py

# Then run tests multiple times (uses cache)
pytest tests/test_dynamic_metar_generation.py -v -x  # stop on first failure
```

## Integration with Conversion

To convert METARs to IWXXM using generated tests:

```python
from src.testing.metar_test_generator import METARTestGenerator
from src.conversion import convert_metar_tac_with_metadata

gen = METARTestGenerator()
cases = gen.diverse_sample(count=10)

for tc in cases:
    # Convert to 2025-2
    iwxxm_xml, validation = convert_metar_tac_with_metadata(
        tc.raw_metar,
        version="2025-2"
    )
    
    if iwxxm_xml:
        print(f"✓ {tc.station_id}")
        # Save or analyze iwxxm_xml
    else:
        print(f"✗ {tc.station_id}: Conversion failed")
        if validation:
            for error in validation.errors:
                print(f"  {error.message}")
```

## Next Steps

1. ✅ **Run Test Generation**: `python3 scripts/generate_test_data.py`
2. ✅ **Check Coverage**: `cat test-data/generated-tests/coverage_report.json`
3. ✅ **Run Tests**: `pytest tests/test_dynamic_metar_generation.py -v`
4. 🔜 **Sprint 3**: Implement semantic validation rules (non-string comparison)
5. 🔜 **Sprint 4**: Dashboard and advanced reporting

## References

- **Sprint 2 Implementation**: [SPRINT2_IMPLEMENTATION_SUMMARY.md](../SPRINT2_IMPLEMENTATION_SUMMARY.md)
- **AviationWeather API**: https://aviationweather.gov/api/
- **OpenAIP Project**: https://www.openaip.net/
- **WMO Codelists**: https://codes.wmo.int/
- **IWXXM Standard**: https://www.wmo.int/pages/prog/wwr/meetings/
