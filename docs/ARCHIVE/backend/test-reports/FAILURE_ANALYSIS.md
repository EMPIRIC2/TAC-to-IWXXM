# METAR→IWXXM Conversion Test Failure Analysis

This directory contains detailed failure reports from the conversion test suite.

## Directory Structure

```
test-reports/
├── local-test-failures/      # JSON diffs from unit tests on static test data
│   ├── {TestCase}_{AmendmentVersion}.json
│   ├── BGBW-282350Z_Amd79-80-2023.json
│   └── ...
├── integration-failures/     # JSON diffs from live API integration tests
│   ├── {StationID}_{Timestamp}.json
│   └── ...
└── FAILURE_ANALYSIS.md       # This file - root cause analysis and solutions
```

## Understanding Failure Reports

Each JSON failure report contains:

```json
{
  "test_case": "BGBW-282350Z",
  "amendment_version": "Amd79-80-2023",
  "status": "FAIL",
  "field_diffs": [
    {
      "path": "/METAR/observation/temperature",
      "type": "TEXT_MISMATCH",
      "expected": "14.5",
      "actual": "14.3",
      "difference": 0.2
    }
  ],
  "lat_lon_diffs": [
    {
      "element_id": "airport-position-1",
      "distance_meters": 150.5,
      "expected_lat": 17.925,
      "expected_lon": -76.789,
      "actual_lat": 17.926,
      "actual_lon": -76.791,
      "status": "OUT_OF_TOLERANCE"
    }
  ],
  "metadata_diffs": [
    {
      "attr": "id",
      "expected": "uuid-12345",
      "actual": "uuid-67890"
    }
  ]
}
```

## Acceptable Differences (Not Errors)

These differences are **normal** and should not cause test failures:

| Category | Reason | Impact |
|----------|--------|--------|
| **UID/ID attributes** | Dynamically generated per conversion | Expected variation |
| **Record/Issue dates** | Current timestamp | Changes on each run |
| **Lat/Lon coordinates** | ±100m tolerance | GPS accuracy, station location precision |
| **Numeric precision** | 0.001 tolerance | Floating point rounding |
| **translatedBulletinID** | Station-specific metadata | Dynamic value |

These should be filtered out and not appear in failure reports.

## Known Failure Patterns

### 1. CAVOK Handling (Amendment Version Dependent)

**Pattern**: CAVOK conditions generate different XML structures across versions

**Status**: Documented, investigating  
**Affected Tests**: Multiple versions  
**Root Cause**: IWXXM 2025-2 encoder vs 2023-1 schema differences

**Example Failure**:
```
Expected: <visibility/>  <!-- omitted for CAVOK -->
Actual:   <visibility>
            <AerodromeHorizontalVisibility>
              <value uom="m">10000</value>
            </AerodromeHorizontalVisibility>
          </visibility>
```

**Solution Path**:
- [ ] Verify IWXXM schema for each version
- [ ] Check GIFTs encoder configuration for CAVOK branch
- [ ] Create amendment-specific encoder parameters
- [ ] Add post-processing for version compatibility

---

### 2. Cloud Layer Optional Elements

**Pattern**: Cloud layers have inconsistent optional element inclusion

**Status**: Investigating  
**Affected Tests**: Amd78-2018, Amd79-80-2021  
**Root Cause**: Optional `cloudType` and `cloudEmissivity` elements

**Example Failure**:
```
Expected: <cloud>
            <CloudLayer>
              <base uom="ft">5000</base>
              <amount>FEW</amount>
            </CloudLayer>
          </cloud>

Actual:   <cloud>
            <CloudLayer>
              <base uom="ft">5000</base>
              <amount>FEW</amount>
              <cloudType>CB</cloudType>  <!-- Extra element -->
            </CloudLayer>
          </cloud>
```

**Solution Path**:
- [ ] Check if cloudType is optional in IWXXM schema
- [ ] Verify GIFTs encoder configuration
- [ ] Add schema compliance validation
- [ ] Document version-specific element requirements

---

### 3. Trend (TEMPO/BECMG) Encoding

**Pattern**: Trend forecasts have complex encoding with many optional elements

**Status**: Needs investigation  
**Affected Tests**: Various, especially complex METAR  
**Root Cause**: WMO amendment differences and TAC parsing variations

**Example Failure**:
```
Expected: <trendForecast>
            <METAR>
              <header/>
              <observation>
                <wind/>
                <visibility/>
              </observation>
            </METAR>
          </trendForecast>

Actual:   <trendForecast>
            <METAR>
              <header/>
              <observation>
                <wind/>
                <visibility/>
                <weather><!-- Extra weather element --></weather>
              </observation>
            </METAR>
          </trendForecast>
```

**Solution Path**:
- [ ] Analyze WMO amendment differences
- [ ] Review TAC trend parsing rules
- [ ] Check GIFTs encoder/decoder synchronization
- [ ] Create trend-specific test fixtures

---

### 4. RVR Special Codes (R88, R99)

**Pattern**: Runway Visual Range special codes don't map cleanly to IWXXM numeric ranges

**Status**: Understanding root cause  
**Affected Tests**: Various  
**Root Cause**: TAC-specific codes unable to represent in XML

| Code | Meaning | IWXXM Challenge |
|------|---------|-----------------|
| R88 | Not operationally significant | Requires special handling or omission |
| R99 | Missing/not reported | Omit RVR or use placeholder |
| P2000 | Greater than 2000m | May be clipped to max value |

**Solution Path**:
- [ ] Research WMO codelist for RVR encoding
- [ ] Check IWXXM schema for special value handling
- [ ] Verify GIFTs encoder RVR processing
- [ ] Create test cases for each special code variant

---

### 5. Weather Phenomena Combinations

**Pattern**: Complex weather (TS+RA, +SGSN) may combine differently

**Status**: Investigating  
**Affected Tests**: Various  
**Root Cause**: Multiple valid XML representations for same TAC

**Example Cases**:
- `+TSRA` → Can be TS + RA separately or combined element
- `SH` (showers) → May or may not include intensity
- `VC` (vicinity) → May affect element grouping

**Solution Path**:
- [ ] Document valid combinations per WMO codes
- [ ] Research IWXXM schema flexibility
- [ ] Check encoder weather grouping logic
- [ ] Create comprehensive weather test matrix

---

## How to Investigate a Failure

When a new failure is discovered:

1. **Locate the report**:
   ```bash
   cat backend/test-reports/local-test-failures/{TestCase}_{Version}.json
   ```

2. **Analyze the diff**:
   - Check `field_diffs` for structural differences
   - Check `lat_lon_diffs` for coordinate issues
   - Ignore metadata_diffs (they're expected)

3. **Find the test data**:
   ```bash
   head -50 data/iwxxm-translation/Amd79-80-2023/metar/{TestCase}.tac
   # Compare with expected XML
   head -50 data/iwxxm-translation/Amd79-80-2023/metar/{TestCase}.xml
   ```

4. **Research the root cause**:
   - Check WMO amendment rules
   - Review GIFTs encoder logic
   - Look at IWXXM schema for element optionality
   - Check if difference is version-specific

5. **Document findings**:
   - Add to `Known Failure Patterns` section above
   - Link to GitHub issue if created
   - Update edge case test in `test_conversion_validation_edge_cases.py`

6. **Create solution**:
   - Implement fix in GIFTs encoder or post-processor
   - Add version-specific handling if needed
   - Verify fix doesn't break other tests

---

## Running Tests and Generating Reports

### Generate all failure reports:
```bash
cd backend
pytest tests/test_metar_pairs_comprehensive.py -v
# Reports saved to: backend/test-reports/local-test-failures/
```

### Analyze specific failures:
```bash
# List all failures
ls backend/test-reports/local-test-failures/*.json | wc -l

# Show failures for specific version
ls backend/test-reports/local-test-failures/*Amd79-80-2023.json

# Pretty-print a report
jq . backend/test-reports/local-test-failures/BGBW-282350Z_Amd79-80-2023.json
```

### Run with error details:
```bash
pytest tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive::test_metar_converts_to_matching_iwxxm -v --tb=long
```

### Integration tests:
```bash
pytest tests/test_eval_endpoint_integration.py -m integration -v
# Reports saved to: backend/test-reports/integration-failures/
```

---

## Tracking Progress

As issues are resolved, update this tracker:

| Issue | Category | Status | Test Impact | PR Link |
|-------|----------|--------|-------------|---------|
| CAVOK element generation | CAVOK | 🔴 Open | 5+ tests | - |
| Cloud layer optional elements | Cloud | 🟡 Investigating | 3 tests | - |
| Trend forecast encoding | Trends | 🔴 Open | 8+ tests | - |
| RVR special codes | RVR | 🟡 Investigating | 2 tests | - |
| Weather combinations | Weather | 🔴 Open | 4+ tests | - |

---

## Integration with CI/CD

### Suggested CI/CD Configurations

**Fast feedback (per-commit):**
```bash
pytest backend/tests/test_metar_pairs_comprehensive.py -v --tb=short
```

**Comprehensive nightly:**
```bash
pytest backend/tests/ -v --tb=short
pytest backend/tests/test_eval_endpoint_integration.py -m integration -v
```

**Failure analysis (on-demand):**
```bash
pytest backend/tests/ -v --tb=long --junit-xml=test-results.xml
# Then analyze JSON reports in test-reports/
```

---

## Contact & Escalation

For questions about specific failures:
- Check the edge case documentation tests
- Review related issue links in this document
- Create GitHub issue with JSON report attached

---

**Last Updated**: 2026-02-11  
**Test Data Versions**: Amd78-2018 (38), Amd79-80-2021 (37), Amd79-80-2023 (34)  
**Total Test Cases**: 109 METAR pairs + integration tests
