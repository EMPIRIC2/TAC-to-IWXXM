# IWXXM Version Comparison Reports

This directory contains JSON reports comparing METAR→IWXXM conversion results across different IWXXM versions.

## Directory Structure

```
test-reports/
├── local-test-failures/     # 2023-1 version (WMO reference baseline)
├── live-test-failures/      # 2025-2 version (aviation-weather-service)
└── integration-failures/    # Integration test failures
```

## Report Format

Each JSON report contains:

```json
{
  "test_case": "KJFK-290000Z",
  "amendment_version": "Amd79-80-2023",
  "status": "PASS|FAIL",
  "field_diffs": [...],
  "lat_lon_diffs": [...],
  "metadata_diffs": [...],
  "expected_xml": "...",
  "actual_xml": "...",
  "generated_at": "2026-02-15T19:37:21.123456"
}
```

## Generating Reports

### Run Tests for 2023-1 (Local/WMO Reference)

```bash
pytest tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive::test_metar_converts_to_matching_iwxxm -v
```

### Run Tests for 2025-2 (Live/Aviation Weather Service)

```bash
pytest tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive::test_metar_converts_to_iwxxm_2025_2 -v
```

### Generate Both and Compare

```bash
# Run both test suites
pytest tests/test_metar_pairs_comprehensive.py::TestMetarConversionComprehensive -v

# Analyze version differences
python scripts/analyze_version_comparisons.py
```

## Comparison Analysis

The `analyze_version_comparisons.py` script provides:

- **Summary Statistics**: Pass/fail counts by version
- **Regressions**: Tests passing in 2023-1 but failing in 2025-2
- **Improvements**: Tests failing in 2023-1 but passing in 2025-2  
- **Persistent Failures**: Common issues across both versions
- **Field Issue Patterns**: Most common field differences

### Example Output

```
================================================================================
IWXXM Version Comparison: Local (2023-1) vs Live (2025-2)
================================================================================

✅ Pass in both versions:          11
⬆️  Pass local, fail live (2025-2): 2
⬇️  Fail local, pass live (2025-2): 19
❌ Fail in both versions:          2
```

## Use Cases

### 1. Schema Migration Planning

Identify which conversions improve/regress when migrating from 2023-1 to 2025-2:

```bash
python scripts/analyze_version_comparisons.py | grep -A20 "IMPROVEMENTS"
```

### 2. Regression Testing

Ensure new changes don't break existing functionality:

```bash
# Before changes
pytest tests/test_metar_pairs_comprehensive.py -v
cp -r test-reports test-reports.baseline

# After changes
pytest tests/test_metar_pairs_comprehensive.py -v
python scripts/analyze_version_comparisons.py
```

### 3. Quality Metrics

Track conversion quality over time:

```bash
# Run weekly and archive results
pytest tests/test_metar_pairs_comprehensive.py -v
mkdir -p metrics/$(date +%Y%m%d)
cp -r test-reports metrics/$(date +%Y%m%d)/
```

### 4. Debugging Specific Failures

Examine detailed diffs for a specific airport:

```bash
# View local (2023-1) report
cat test-reports/local-test-failures/KJFK-290000Z_Amd79-80-2023.json | jq '.field_diffs'

# View live (2025-2) report
cat test-reports/live-test-failures/KJFK-290000Z_Amd79-80-2023-2025-2.json | jq '.field_diffs'

# Compare full XML
diff <(cat test-reports/local-test-failures/KJFK-290000Z_Amd79-80-2023.json | jq -r '.actual_xml') \
     <(cat test-reports/live-test-failures/KJFK-290000Z_Amd79-80-2023-2025-2.json | jq -r '.actual_xml')
```

## Automated Comparison

### GitHub Actions Integration

A workflow runs version comparison on:
- Weekly schedule (Sundays)
- Manual trigger
- Changes to conversion logic

Results are uploaded as artifacts and commented on PRs.

## Report Retention

- Local reports: Committed to repository
- Live reports: Generated per-run (not committed)
- Archive old reports to `metrics/` directory for historical analysis

## Interpreting Results

### Pass Status

- **PASS**: All fields match within tolerance
  - Lat/lon within 100m
  - Numeric values within 0.001 precision
  - Dynamic attributes (IDs, timestamps) ignored

### Fail Status

- **FAIL**: One or more fields differ beyond tolerance
  - Check `field_diffs` for structural differences
  - Check `lat_lon_diffs` for coordinate precision issues
  - Check `metadata_diffs` for attribute differences

### Common Patterns

**Metadata Differences** (acceptable):
- Translation center name/designator
- Translation/bulletin timestamps
- Generated UUIDs (gml:id)

**Field Differences** (investigate):
- Trend forecast time periods
- Airport metadata (name, IATA code)
- Weather phenomenon encoding

**Coordinate Differences** (acceptable if <100m):
- Database precision variations
- Datum conversion differences

## Contributing

When adding new test data:

1. Add TAC/XML pairs to `data/iwxxm-translation/{version}/metar/`
2. Run both test suites to generate reports
3. Run comparison analysis to verify no regressions
4. Document any expected differences in this README

## Troubleshooting

### No Reports Generated

```bash
# Ensure directories exist
mkdir -p test-reports/{local-test-failures,live-test-failures}

# Run tests with verbose output
pytest tests/test_metar_pairs_comprehensive.py -xvs
```

### Analysis Script Fails

```bash
# Check Python path
python3 scripts/analyze_version_comparisons.py

# Run from backend directory
cd backend && python scripts/analyze_version_comparisons.py
```

### Missing Dependencies

```bash
# Install test dependencies
uv pip install -e ".[test]"
```

## Related Documentation

- [Testing Strategy](../docs/testing/TESTING_STRATEGY.md)
- [IWXXM Version Switching](../docs/domain/iwxxm/IWXXM_VERSION_SWITCHING.md)
- [Validation Implementation](../VALIDATION_IMPLEMENTATION_SUMMARY.md)
