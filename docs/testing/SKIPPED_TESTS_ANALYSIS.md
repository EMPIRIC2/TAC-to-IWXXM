# Skipped Tests Analysis

## Overview
The test suite includes intentionally skipped tests across multiple test files. These skips are categorized by reason and provide documentation of known limitations, placeholder tests, and architectural constraints.

## Summary Statistics
- **Total Test Files with Skips:** ~15 files
- **Total Skipped Tests:** ~50+ tests
- **Skip Categories:** 7 main categories (see below)

---

## Skip Categories

### 1. **Placeholder Edge Case Tests** (12 tests)
**File:** `tests/test_conversion_validation_edge_cases.py`

These are intentionally skipped placeholder tests for documenting known conversion failures and edge cases where:
- The generated IWXXM is technically valid but structurally differs from reference
- Root cause is understood but not yet resolved
- Tests can be run to track failure patterns across versions

**Tests:**
- `test_cavok_visibility_element_generation` - CAVOK visibility handling differences
- `test_cloud_type_optional_element_inclusion` - Cloud layer encoding variations
- `test_trend_tempo_becmg_encoding_consistency` - Trend encoding differences
- `test_rvr_special_code_r88_r99_encoding` - RVR special codes
- `test_rvr_variable_range_encoding` - Variable RVR ranges
- `test_weather_intensity_modifier_encoding` - Weather intensity modifiers
- `test_heavy_thunderstorm_precipitation_combination` - Complex weather combinations
- `test_altimeter_unit_conversion_precision` - Altimeter precision issues
- `test_wind_shear_altitude_layer_encoding` - Wind shear altitude encoding
- `test_amd78_2018_optional_element_presence` - Amendment 78-2018 version differences
- `test_amd79_80_2021_vs_2023_element_changes` - Amendment version element changes
- `test_known_failure_template` - Example known failure template

**Reason:** Tracked known failures - Use `@pytest.mark.edge_case` mark to run: `pytest -m edge_case`

---

### 2. **Legacy Function Replacements** (1 test)
**File:** `tests/test_conversion_edge_cases.py`

**Test:** `test_lookup_aerodrome_returns_none_when_db_missing`

**Reason:** "Legacy function `_lookup_aerodrome` replaced by GiftsLocationDBAdapter"

**Context:** The old CSV-based aerodrome lookup has been superseded by the GiftsLocationDBAdapter. Since this is a legacy function, the test for the old behavior is no longer relevant.

---

### 3. **Graceful Degradation Incompatibilities** (2 tests)
**File:** `tests/test_conversion_edge_cases.py`

**Tests:**
- `test_convert_with_decoder_construction_failure`
- `test_convert_with_decoding_error`

**Reason:** "Test incompatible with graceful degradation in conversion pipeline"

**Context:** The conversion pipeline now handles errors gracefully with fallbacks (e.g., OpenAIP integration fallback). These tests expect exceptions to be raised, which conflicts with the new error handling strategy.

---

### 4. **Module-Level Patching Requirements** (1 test)
**File:** `tests/test_conversion_edge_cases.py`

**Test:** `test_convert_with_gifts_unavailable`

**Reason:** "Patching GIFTs unavailability requires module-level patching before import"

**Context:** GIFTs modules are imported at the module level in the conversion utilities, making it impossible to patch their unavailability during test execution without restructuring imports.

---

### 5. **Live API & Network Tests** (2 tests - runtime skip)
**File:** `tests/test_aviationweather_live_api.py`

**Tests:**
- Multiple tests in the live API suite that skip at runtime due to:
  - Failed METAR fetches from AviationWeather.gov API
  - Network connectivity issues
  - API service unavailability

**Reason:**
- `pytest.skip(f"Failed to fetch METAR for {icao_code}: {e}")` - API fetch failed
- `pytest.skip(f"No METAR data available for {icao_code}")` - No data returned from API
- `@pytest.mark.skip("Live API test - network dependent, may fail in CI/CD")` - Integration test marked to skip in CI/CD

**Context:** These tests require external API calls which may fail in CI/CD environments or when network is unavailable. The `test_live_metar_conversion_2025_2` test is the main integration test that fetches live METARs.

---

### 6. **Schema/Data Availability** (Variable)
**Files:** Multiple files including:
- `tests/test_schema_registry.py` - Schema submodules not initialized (git submodules)
- `tests/test_xsd_validator.py` - IWXXM schemas not available
- `tests/test_docker_schematron_container.py` - Schema or test XML files not found
- `tests/test_metar_pairs_comprehensive.py` - No METAR pairs available

**Reason:** Missing git submodules or test data files

**Context:** These tests skip gracefully when required resources (IWXXM schema git submodules, test data files) are not available in the environment.

Example:
```python
pytest.skip("IWXXM schemas not available (git submodule not initialized)")
pytest.skip("Schema submodules not initialized")
```

---

### 7. **Data Generation/Availability** (Variable)
**Files:**
- `tests/test_dynamic_metar_generation.py` - No METARs found for region/phenomenon
- `tests/test_task_3_1_integration.py` - Unable to generate test cases
- `tests/test_task_3_2_integration.py` - No multi-layer cloud cases
- `tests/test_task_3_5_extended_coverage.py` - No test cases generated

**Reason:** Generated test data doesn't contain required properties

**Context:** These tests generate METAR data from CSV files and skip when the generated set doesn't contain specific phenomena (e.g., "No METARs found for region GLOBAL").

---

### 8. **Known Mocking Limitations** (1 test)
**File:** `tests/test_coverage_boost.py`

**Test:** One test related to aerodrome lookup

**Reason:** "Mock not working due to multiple data source fallbacks in `_lookup_aerodrome`"

**Context:** The function has multiple fallback mechanisms, making it difficult to mock specific failure scenarios.

---

### 9. **Unsupported Functionality** (1 test)
**File:** `tests/test_roundtrip.py`

**Test:** `test_*` (round-trip reverse decoding)

**Reason:** "XML→TAC reverse decoding not supported by GIFTs"

**Context:** The test attempts to validate round-trip conversion (METAR→IWXXM→METAR) but GIFTs doesn't support reverse decoding.

---

### 10. **Auth Service Skips** (7 tests)
**File:** `tests/test_auth_middleware.py` (Auth service)

**Reason:** "Requires proper Supabase mock or live backend"

**Context:** Auth middleware tests require a properly configured Supabase backend or complex mocking infrastructure that isn't available in all test environments.

---

## Recommendations

### High Priority - Consider Enabling
1. **Live API Tests** - Consider enabling in staging environments with proper API mocking
2. **Schema Availability Tests** - Ensure git submodules are initialized: `git submodule update --init --recursive`
3. **Edge Case Tests** - These are valuable for tracking known issues. Consider maintaining them with clear issue references

### Medium Priority - Near-term Improvements
1. **Refactor for Patchability** - Restructure module-level imports to enable testing of GIFTs unavailability scenarios
2. **Graceful Error Testing** - Update tests that expect exceptions to align with new graceful degradation strategy
3. **Mock Infrastructure** - Improve Supabase mocking for auth tests

### Low Priority - Documentation
1. **Add Issue References** - Link skipped tests to GitHub issues for tracking
2. **Update Comments** - Ensure each skip reason includes suggestion for enablement conditions

---

## How to Run Specific Test Categories

### Run only edge case tests:
```bash
pytest -m edge_case -v
```

### Run only live API tests:
```bash
pytest tests/test_aviationweather_live_api.py -v -m live_api
```

### Run all tests including skipped (to see which ones):
```bash
pytest tests/ -v --tb=no -q 2>&1 | grep SKIP
```

### Run specific test file with verbose skip reasons:
```bash
pytest tests/test_conversion_validation_edge_cases.py -v --tb=short
```

---

## Files with Skipped Tests Summary

| File | Skip Count | Primary Reason |
|------|-----------|-----------------|
| `test_conversion_validation_edge_cases.py` | 12 | Placeholder edge cases |
| `test_conversion_edge_cases.py` | 4 | Legacy, patchability, graceful degradation |
| `test_aviationweather_live_api.py` | 2+ | Network/API data availability |
| `test_dynamic_metar_generation.py` | 3+ | No matching test data |
| `test_task_3_*.py` | 3+ | Generated test cases unavailable |
| `test_schema_registry.py` | 4 | Schema submodules not initialized |
| `test_auth_middleware.py` | 7 | Supabase infrastructure required |
| `test_roundtrip.py` | 1 | Unsupported reverse decode |
| Others | ~5+ | Various (missing data, files, etc) |

---

## Next Steps

1. **Initialize Schema Submodules** - Run `git submodule update --init --recursive` to enable schema validation tests
2. **Document Issue References** - Add GitHub issue numbers to placeholder edge case tests
3. **Implement Graceful Degradation Tests** - Update error-handling tests to match new pipeline semantics
4. **Set Up API Mocking** - Create fixtures for live API tests using recorded responses
