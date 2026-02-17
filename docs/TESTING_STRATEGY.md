# METAR→IWXXM Conversion Test Strategy

Comprehensive guide to testing the METAR to IWXXM conversion system using static test data and live API integration.

**Date**: 2026-02-13  
**Test Data**: 34 METAR pairs from current IWXXM version  
**Amendment Version**: Amd79-80-2023 (IWXXM 2023-1/2025-2)

---

## Overview

The test strategy is a **two-tier approach**:

1. **Local Unit Tests** - Fast, deterministic tests using static .tac/.xml pairs
2. **Integration Tests** - Real-world validation hitting live Aviation Weather Service API

Both tiers use **structured failure reporting** with JSON diffs for root cause analysis and systematic resolution of edge cases.

### Key Principles

✅ **Comprehensive** - All 34 test pairs from supported IWXXM versions  
✅ **Deterministic** - Units use static data; integration tests are optional  
✅ **Transparent** - Failures generate detailed diff reports, not just pass/fail  
✅ **Version-Aware** - Tests current IWXXM versions (2025-2, 2023-1) for compliance  
✅ **Traceable** - Edge cases documented with root cause and solution paths

**Deprecated**: Pre-2023 versions (2021-2, 2018, 2016) test data removed as of 2026-02-13.

---

## Test Data Organization

### Location

```
data/iwxxm-translation/
└── Amd79-80-2023/   # 2023 Amendment (34 METAR pairs, IWXXM 2023-1/2025-2)
    ├── metar/
    │   ├── BGBW-282350Z.tac    ← METAR TAC input
    │   ├── BGBW-282350Z.xml    ← Expected IWXXM output
    │   ├── BGGH-282350Z.tac
    │   ├── BGGH-282350Z.xml
    │   └── ... (32 more pairs)
    └── taf/, ...
```

**Deprecated Data Removed**: Amd78-2018/ and Amd79-80-2021/ directories were removed on 2026-02-13 when versions 2018, 2021-2 were deprecated.

### Test Case Format

Each test case is a pair of files:

| File | Content | Example |
|------|---------|---------|
| `{STATION}-{TIMESTAMP}.tac` | METAR TAC string (input) | `BGBW 282350Z 06008KT 9999 ...=` |
| `{STATION}-{TIMESTAMP}.xml` | IWXXM XML output (expected) | `<METAR>...</METAR>` |

The test converts `.tac` → XML and compares against `.xml`.

---

## Running Tests

### All Local Tests (Recommended for CI/CD)

```bash
cd backend
pytest tests/test_metar_pairs_comprehensive.py -v

# Expected output:
# PASSED tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive::test_metar_converts_to_matching_iwxxm[Amd79-80-2023_BGBW-282350Z] - ...
# PASSED tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive::test_metar_converts_to_matching_iwxxm[Amd79-80-2023_BGGH-282350Z] - ...
# ... (34 tests total)
```

### By Amendment Version

```bash
# 2023 version (all current tests)
pytest tests/test_metar_pairs_comprehensive.py -v -k "Amd79-80-2023"

# All comprehensive tests
pytest tests/test_metar_pairs_comprehensive.py -v
```

### With Coverage

```bash
pytest tests/test_metar_pairs_comprehensive.py --cov=src --cov-report=html
# Reports: htmlcov/index.html
```

### Integration Tests (Requires Network)

```bash
# Smoke tests (3 stations, ~30 seconds)
pytest tests/test_eval_endpoint_integration.py -m integration --smoke

# Full integration (10+ stations, ~2-3 minutes)
pytest tests/test_eval_endpoint_integration.py -m integration -v

# Mock-only (no network needed)
pytest tests/test_eval_endpoint_integration.py::TestIntegrationWithMocks -m integration
```

### Edge Cases (Known Failures)

```bash
# Show all known failures
pytest tests/test_conversion_validation_edge_cases.py -m edge_case -v

# These are marked @pytest.mark.xfail or @pytest.mark.skip
# They're tracked for investigation but don't fail the test suite
```

### Fast Mode (Unit Tests Only, ~30 seconds)

```bash
pytest tests/test_metar_pairs_comprehensive.py tests/test_conversion_validation_edge_cases.py -v -m "not integration"
```

---

## Acceptable Differences (Tolerance Rules)

The test suite allows these differences between expected and converted XML:

### 1. **Dynamic Attributes** (Completely Ignored)

```xml
<!-- These are dynamically generated and differ on each run -->
gml:id="..."           <!-- UID -->
id="..."               <!-- ID -->
schemaLocation="..."   <!-- Schema reference -->
translatedBulletinID="..." <!-- Station bulletin -->
```

**Rationale**: Runtime-generated metadata changes on each conversion.

### 2. **Timestamps & Dates** (Ignored)

```xml
<!-- Current timestamp at conversion time -->
<timestamp>2026-02-11T12:34:56Z</timestamp>
<validTime>
  <gml:TimePeriod>
    <gml:beginPosition>2026-02-11T12:30:00Z</gml:beginPosition>
    <gml:endPosition>2026-02-11T13:30:00Z</gml:endPosition>
  </gml:TimePeriod>
</validTime>
```

**Rationale**: METAR is always issued at current time; exact timestamp varies.

### 3. **Lat/Lon Coordinates** (±100 meter tolerance)

```xml
<AirportPosition gml:id="airport-1">
  <gml:pos>17.925 -76.789</gml:pos>  <!-- Expected: 17.925, -76.789 -->
  <!-- Actual can be: 17.926, -76.791 (distance 150m) ✓ -->
  <!-- Actual can be: 17.935, -76.800 (distance 1.2km) ✗ -->
</AirportPosition>
```

**Rationale**: GPS accuracy ±50m; airport location data precision ±100m acceptable.  
**Calculation**: Haversine distance formula between lat/lon pairs.  
**Tolerance**: 100 meters (configurable in tests).

### 4. **Numeric Precision** (0.001 tolerance)

```xml
<!-- Temperature: 14.50 vs 14.51 ✓ -->
<!-- Altimeter: 1014.50 vs 1014.51 hPa ✓ -->
<!-- Wind: 14.0 vs 14.001 kt ✓ -->
<!-- Difference > 0.001: ✗ -->
```

**Rationale**: Floating point rounding in unit conversion.  
**Example**: Miles→meters conversion: 6 SM = 11112m ≈ 11112.0m

---

## Failure Reports

When a test fails, a detailed JSON report is generated:

### Location

```
backend/test-reports/local-test-failures/{TestCase}_{AmendmentVersion}.json
backend/test-reports/integration-failures/{StationID}_{Timestamp}.json
```

### Example Report

```json
{
  "test_case": "BGBW-282350Z",
  "amendment_version": "Amd79-80-2023",
  "status": "FAIL",
  "field_diffs": [
    {
      "path": "/METAR/observation/cloud",
      "type": "EXTRA_CHILD",
      "child_tag": "cloudType",
      "index": 1
    },
    {
      "path": "/METAR/observation/wind/direction",
      "type": "TEXT_MISMATCH",
      "expected": "060",
      "actual": "061",
      "difference": 1.0
    }
  ],
  "lat_lon_diffs": [
    {
      "element_id": "airport-position-1",
      "distance_meters": 45.2,
      "expected_lat": 17.925,
      "expected_lon": -76.789,
      "actual_lat": 17.9253,
      "actual_lon": -76.7892,
      "status": "WITHIN_TOLERANCE"  // ← Not an error
    }
  ],
  "metadata_diffs": []  // ← Always empty (ignored attributes)
}
```

### Reading the Report

| Field | Meaning | Action |
|-------|---------|--------|
| `field_diffs` | Structural XML differences | **Investigate** - these are real divergences |
| `lat_lon_diffs` with `WITHIN_TOLERANCE` | Coordinates differ but acceptably | **OK** - ignore |
| `lat_lon_diffs` with `OUT_OF_TOLERANCE` | Coordinates differ > 100m | **Investigate** |
| `lat_lon_diffs` with `MISSING_IN_ACTUAL` | Expected position missing | **Investigate** |
| `metadata_diffs` | Empty (always ignored) | **OK** - expected |

---

## Known Failure Patterns

See [backend/test-reports/FAILURE_ANALYSIS.md](test-reports/FAILURE_ANALYSIS.md) for detailed analysis of known issues including:

- **CAVOK** - CAVOK handling differs across amendment versions
- **Cloud Layers** - Optional `cloudType` element inclusion varies
- **Trend Forecasts** - TEMPO/BECMG complex encoding differences
- **RVR Special Codes** - R88, R99 codes don't map to IWXXM numeric ranges
- **Weather Phenomena** - Complex weather combinations have multiple valid representations
- **Altimeter Precision** - Unit conversion rounding differences
- **Wind Shear** - Altitude layer encoding varies
- **Amendment Versions** - Amd78-2018 vs newer versions schema differences

Each pattern includes:
- Example failure showing expected vs actual
- Root cause explanation
- Solution path with actionable steps

---

## Test Statistics

### Test Counts by Amendment

| Amendment | Version | Test Cases | Status |
|-----------|---------|------------|--------|
| Amd78-2018 | 2018 | 38 | ✓ All tests run |
| Amd79-80 | 2021-2 | 37 | ✓ All tests run |
| Amd79-80 | 2023-1 | 34 | ✓ All tests run |
| **Total** | - | **109** | **✓** |

### Test Execution Time

| Category | Count | Time | Per-Test |
|----------|-------|------|----------|
| Unit (local data) | 109 | ~45s | ~0.4s |
| Integration (3 stations) | 3 | ~30s | ~10s |
| Integration (10+ stations) | 10+ | ~2min | ~12s |
| Full suite (with coverage) | 130+ | ~2min | ~0.9s |

### CI/CD Recommendations

```yaml
# .github/workflows/test.yml
jobs:
  test-fast:
    # Per-commit - unit tests only
    run: pytest backend/tests/test_metar_pairs_comprehensive.py -v
    timeout: 2m

  test-comprehensive:
    # Nightly/weekly - include integration
    run: pytest backend/tests/ -m "not slow" -v
    timeout: 5m

  test-full:
    # Monthly - all including slow integration
    run: pytest backend/tests/ -v
    timeout: 10m
```

---

## Investigating Failures

### Step 1: Locate the Report

```bash
# List all failures
ls -lh backend/test-reports/local-test-failures/*.json | head -10

# Check specific test case
cat backend/test-reports/local-test-failures/BGBW-282350Z_Amd79-80-2023.json | jq .
```

### Step 2: Analyze the Diff

Focus on `field_diffs` that show actual XML differences:

```bash
# Pretty-print diffs
jq '.field_diffs | .[0:5]' backend/test-reports/local-test-failures/*.json

# Filter by type
jq '.field_diffs[] | select(.type == "MISSING_CHILD")' backend/test-reports/local-test-failures/*.json
```

### Step 3: Examine Test Data

```bash
# Show the METAR input
head -5 data/iwxxm-translation/Amd79-80-2023/metar/BGBW-282350Z.tac

# Show expected XML output (first 50 lines)
head -50 data/iwxxm-translation/Amd79-80-2023/metar/BGBW-282350Z.xml | xmllint --format -

# Run conversion manually
python3 << 'EOF'
from backend.src.utilities.conversion import convert_metar

tac = open("data/iwxxm-translation/Amd79-80-2023/metar/BGBW-282350Z.tac").read().strip()
xml = convert_metar(tac)
print(xml)
EOF
```

### Step 4: Root Cause Analysis

Check `test_conversion_validation_edge_cases.py` for documented patterns:

```bash
# List documented patterns
grep -A 10 "class Test" backend/tests/test_conversion_validation_edge_cases.py

# Search for issue related to your failure
grep -r "CAVOK\|cloudType\|trend" backend/tests/test_conversion_validation_edge_cases.py
```

### Step 5: Create GitHub Issue

If root cause is unknown, create an issue with:

1. Test case name and amendment version
2. JSON diff report (copy from test-reports/)
3. Expected vs actual XML snippets
4. Hypothesis about root cause
5. Link to relevant WMO amendment rules

---

## Comparison Logic

### XML Comparison Algorithm

```python
compare_xml_with_tolerance(
    expected_elem,      # From reference .xml file
    actual_elem,        # Converted XML output
    test_case,          # Test identifier
    amendment_version,  # For reporting
    lat_lon_tolerance_m = 100.0,    # ±100 meters
    ignore_attrs = {
        'id', 'gml:id', 'schemaLocation',
        'translatedBulletinID'
    }
)
# Returns: DiffReport(status='PASS'|'FAIL', field_diffs=[...], lat_lon_diffs=[...])
```

### Element-by-Element Comparison

1. **Tag names** (ignoring namespaces) - must match exactly
2. **Attributes** - must match except for ignored/dynamic ones
3. **Text content** - must match with 0.001 numeric tolerance
4. **Child elements** - order must match, counts must match
5. **Lat/Lon coordinates** - haversine distance ≤ 100m allowed

### Namespace Handling

```xml
<!-- These are equivalent -->
<METAR xmlns="http://www.opengis.net/gml/3.2.1">
<gml:METAR xmlns:gml="http://www.opengis.net/gml/3.2.1">

<!-- Test uses local-name() for comparison -->
_local("gml:METAR") == "METAR" == _local("{http://...}METAR")  ✓
```

---

## Extending Tests

### Adding New Test Data

```bash
# 1. Create test pair
echo "METAR KJFK 121851Z 09014G25KT 10SM FEW250 23/14 A3012 RMK AO2=" > \
  data/iwxxm-translation/Amd79-80-2023/metar/KJFK-121851Z.tac

# 2. Generate expected output
python3 -c "
from backend.src.utilities.conversion import convert_metar
print(convert_metar(open('...KJFK-121851Z.tac').read()))
" > data/iwxxm-translation/Amd79-80-2023/metar/KJFK-121851Z.xml

# 3. Test will automatically discover and run it
pytest tests/test_metar_pairs_comprehensive.py -k "KJFK-121851Z" -v
```

### Adding Regression Tests

When fixing a bug, add a test for it:

```python
# In test_conversion_validation_edge_cases.py
@pytest.mark.edge_case
def test_regression_cavok_element_generation_fix():
    """Regression test: CAVOK now generates proper elements per issue #XXX"""
    # Your test here
    pass
```

### Custom Tolerance Rules

Modify tolerance in `_comparative_xml_utils.py`:

```python
# Change lat/lon tolerance to 50m
compare_xml_with_tolerance(
    expected, actual,
    lat_lon_tolerance_m=50.0  # ← Changed from 100.0
)

# Add numeric tolerance for specific field
if path == "/METAR/observation/temperature":
    tolerance = 0.1  # ±0.1°C for temperature
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test METAR Conversion
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: cd backend && pip install -e ".[dev]"
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/test_metar_pairs_comprehensive.py -v --tb=short
          pytest tests/test_conversion_validation_edge_cases.py -m "not integration" -v
      
      - name: Collect failure reports
        if: failure()
        run: |
          tar -czf test-reports.tar.gz backend/test-reports/
          
      - name: Upload reports
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: test-reports.tar.gz

  test-integration:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: cd backend && pip install -e ".[dev]"
      
      - name: Run integration tests (mocked)
        run: |
          cd backend
          pytest tests/test_eval_endpoint_integration.py::TestIntegrationWithMocks -v
```

---

## Troubleshooting

### Test Discovery Issues

```bash
# Verify pytest finds all tests
pytest backend/tests/test_metar_pairs_comprehensive.py --collect-only
# Should show: 109 test cases collected

# If missing, check:
# 1. data/iwxxm-translation/ exists and has metar/ subdirs
# 2. *.tac and *.xml files present
# 3. METAR_PAIRS = _collect_metar_pairs(DATA_ROOT) runs without error
```

### Import Errors

```bash
# Ensure paths are correct
cd backend
python -c "from tests._comparative_xml_utils import compare_xml_with_tolerance; print('✓')"

# Check sys.path
pytest --co -q 2>&1 | head -20
```

### Slow Tests

```bash
# Profile test execution
pytest --durations=10 tests/test_metar_pairs_comprehensive.py

# Typical: 0.4-0.5s per test; > 2s indicates conversion problem
```

### Report Directory Permissions

```bash
# Ensure report directory is writable
mkdir -p backend/test-reports/local-test-failures
chmod 755 backend/test-reports/
```

---

## References

- **WMO Amendment 78-2018**: [data/iwxxm-translation/Amd78-2018/](../../../data/iwxxm-translation/Amd78-2018/)
- **WMO Amendment 79-80-2021**: [data/iwxxm-translation/Amd79-80-2021/](../../../data/iwxxm-translation/Amd79-80-2021/)
- **WMO Amendment 79-80-2023**: [data/iwxxm-translation/Amd79-80-2023/](../../../data/iwxxm-translation/Amd79-80-2023/)
- **IWXXM Specification**: [schemas/iwxxm/](../../../schemas/iwxxm/)
- **GIFTs Encoder/Decoder**: [GIFTs/](../../../GIFTs/)
- **Test Utilities**: [backend/tests/_xml_utils.py](../../tests/_xml_utils.py)
- **Failure Analysis**: [backend/test-reports/FAILURE_ANALYSIS.md](test-reports/FAILURE_ANALYSIS.md)

---

## API Testing Infrastructure (2026-02-16 Update)

### Overview

In addition to conversion testing, we have implemented comprehensive API testing infrastructure covering all endpoints across multiple testing layers:

### Testing Pyramid

```
        /\
       /  \      Live API (Production Monitoring)
      /____\
     /      \    E2E Tests (Full Stack)
    /________\
   /          \  Integration Tests (Mocked Services)
  /____________\
 /______________\ Unit Tests (Component Testing)
       |
    Smoke Tests (Critical Path)
```

### Test Layers

#### 1. Unit Tests (`pytest -m unit`)
- **Runtime**: < 5 minutes
- **Purpose**: Isolated component testing
- **Coverage**: > 90%
- **When**: Every commit

#### 2. Integration Tests (`pytest -m integration`)
- **Runtime**: < 10 minutes
- **Purpose**: API endpoints with mocked services
- **Coverage**: > 85%
- **When**: Pull requests, before merge

**New Comprehensive Test Files (2026-02-16)**:
- **`test_evaluation_endpoints_comprehensive.py`** - All evaluation router endpoints
  - Job creation (single, random, all modes)
  - Job listing with pagination
  - Job status retrieval
  - Job results with filtering
  - Background task lifecycle
  - Authorization testing
  
- **`test_icao_opmet_admin.py`** - ICAO OPMET statistics with admin auth
  - Translation Centre identification
  - Statistics queries with filters (region, version, airport)
  - Recent statistics endpoints
  - Regional aggregation
  - Admin role enforcement
  - Pagination testing
  - Date range validation

#### 3. Smoke Tests (`pytest -m smoke`)
- **Runtime**: ~30 seconds
- **Purpose**: Rapid CI/CD validation
- **Coverage**: Critical happy path
- **When**: Every PR, pre-deployment

**Test File**: `test_smoke.py`

**Coverage**:
- ✅ Health check responds
- ✅ Authentication works
- ✅ Single METAR conversion
- ✅ Single validation request
- ✅ Evaluation job creation
- ✅ Statistics endpoints accessible
- ✅ Error handling basics

#### 4. Live API Health Checks (`pytest -m live_api`)
- **Runtime**: < 2 minutes
- **Purpose**: Production monitoring
- **When**: Continuous, post-deployment

**Test File**: `test_live_api_health.py`

**Configuration**:
```bash
export LIVE_API_URL=https://api.example.com
export LIVE_API_TOKEN=your_jwt_token
pytest -m live_api
```

**Monitors**:
- ✅ API reachability
- ✅ Response times (< 5s for conversions)
- ✅ Health endpoints
- ✅ Authentication
- ✅ Critical path workflows
- ✅ Concurrent request handling

#### 5. End-to-End Tests (`pytest -m e2e`)
- **Runtime**: < 15 minutes
- **Purpose**: Full stack with real services
- **When**: Pre-release, staging
- **Status**: Coming soon

### Test Organization

```
backend/tests/
├── README.md                                    ← Testing guide
├── test_fixtures.py                             ← Shared fixtures
├── conftest.py                                  ← Pytest configuration
│
├── test_smoke.py                                ← Smoke tests
├── test_live_api_health.py                      ← Live API monitoring
│
├── test_evaluation_endpoints_comprehensive.py   ← Evaluation endpoints (NEW)
├── test_icao_opmet_admin.py                    ← ICAO OPMET admin auth (NEW)
│
├── test_api.py                                  ← Core API tests
├── test_api_comprehensive.py                    ← Extended API tests
├── test_validation_router.py                    ← Validation endpoints
├── test_eval_endpoint_integration.py            ← Evaluation integration
├── test_icao_opmet.py                          ← ICAO OPMET tests
│
└── test_metar_pairs_comprehensive.py            ← Conversion tests (from above)
```

### Running API Tests

```bash
# All tests
pytest

# By category
pytest -m unit
pytest -m integration
pytest -m smoke
pytest -m live_api
pytest -m "not slow"

# Specific test files
pytest tests/test_evaluation_endpoints_comprehensive.py -v
pytest tests/test_icao_opmet_admin.py -v
pytest tests/test_smoke.py -v

# With coverage
pytest --cov=src --cov-report=html
```

### Test Fixtures

Common fixtures provided in `test_fixtures.py`:

#### Authentication
- `client` - TestClient with regular user auth
- `admin_client` - TestClient with admin auth
- `unauthenticated_client` - TestClient without auth

#### Service Mocks
- `mock_supabase_client` - Mock database client
- `mock_statistics_service` - Mock statistics service
- `mock_aviation_weather_client` - Mock Aviation Weather API

#### Sample Data
- `sample_metars` - Dictionary of METAR examples
- `sample_iwxxm` - Sample IWXXM XML
- `sample_station_ids` - International airport codes

#### Live API
- `live_api_client` - httpx AsyncClient for real API testing

### Coverage Targets

| Component | Target | Status |
|-----------|--------|--------|
| Conversion endpoints | 95% | ✅ Achieved |
| Validation endpoints | 95% | ✅ Achieved |
| Evaluation endpoints | 95% | ✅ New tests added |
| ICAO OPMET endpoints | 90% | ✅ Admin auth tests added |
| Services | 85% | ⚠️ In progress |

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: API Tests

on: [push, pull_request]

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run smoke tests
        run: pytest -m smoke
  
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: pytest -m integration
  
  live-api-health:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Check production API
        env:
          LIVE_API_URL: ${{ secrets.LIVE_API_URL }}
          LIVE_API_TOKEN: ${{ secrets.LIVE_API_TOKEN }}
        run: pytest -m live_api
```

### Monitoring and Alerts

Live API health checks can be configured for continuous monitoring:

**Scheduled Workflow** (`.github/workflows/api-health-check.yml`):
- Runs every 15 minutes
- Tests production API endpoints
- Reports response times
- Sends alerts on failure

**Performance Thresholds**:
- Health check: < 2s
- Version info: < 2s
- Single conversion: < 5s
- Validation: < 10s

### Documentation

- **[backend/tests/README.md](../../backend/tests/README.md)** - Detailed testing guide
- **[test_fixtures.py](../../backend/tests/test_fixtures.py)** - Fixture documentation
- **Current document** - Overall strategy

---

**Version**: 2.0  
**Last Updated**: 2026-02-16  
**Maintainers**: Backend Team

