# Test Organization Guide

## Overview

The test suite has been reorganized into logical subdirectories to improve maintainability, clarity, and navigation. All 1,090+ tests are organized by domain and functionality.

## Directory Structure

```
tests/
├── conftest.py                          # Global pytest configuration & fixtures
├── test_fixtures.py                     # Shared test fixtures
│
├── _comparative_xml_utils.py            # XML comparison utilities for tests
├── _integration_helpers.py              # Integration test helpers
├── _xml_utils.py                        # XML utilities for tests
│
├── unit/                                # Unit tests (isolated components)
│   └── test_tac_parser.py              # TAC parsing unit tests
│
├── api/                                 # API endpoint tests
│   ├── test_api.py
│   ├── test_api_comprehensive.py        # CORS, routing, dependencies
│   ├── test_api_error_handling.py
│   ├── test_api_schema_status.py
│   └── test_api_validation.py
│
├── conversion/                          # METAR→IWXXM conversion tests
│   ├── test_convert.py                 # Basic conversion
│   ├── test_conversion_integration.py  # Conversion with validation
│   ├── test_conversion_edge_cases.py
│   ├── test_conversion_validation_edge_cases.py
│   ├── test_roundtrip.py               # Round-trip XML conversion
│   └── test_utilities_conversion.py    # Utility function tests
│
├── validation/                          # XML/SCHEMATRON validation tests
│   ├── test_validation_service.py
│   ├── test_validation_orchestrator.py
│   ├── test_validation_router.py       # Validation endpoint tests
│   ├── test_validation_e2e.py
│   ├── test_validation_changes.py
│   ├── test_semantic_validation.py
│   ├── test_schematron_validation_suite.py
│   ├── test_iwxxm_validation.py        # IWXXM-specific validation
│   └── test_airport_validation_integration.py
│
├── iwxxm/                               # IWXXM and XML schema tests
│   ├── test_iwxxm_versions_rc.py       # Version compatibility
│   ├── test_iwxxm_examples.py          # Example conversions
│   ├── test_xml_version_utils.py       # XML version utilities
│   ├── test_wmo_canonical_examples.py  # WMO examples
│   ├── test_schemas.py                 # Schema validation
│   ├── test_evaluation_schemas.py
│   └── test_elevation_version_formatting.py
│
├── services/                            # Data service tests
│   ├── test_airport_data_service.py
│   ├── test_database_service.py
│   ├── test_statistics_service.py
│   └── test_station_sampler.py
│
├── evaluation/                          # Evaluation system tests
│   ├── test_evaluation_endpoints_comprehensive.py
│   ├── test_evaluation_service_comprehensive.py
│   ├── test_evaluation_system.py
│   ├── test_icao_opmet.py              # ICAO OPMET reports
│   └── test_icao_opmet_admin.py        # Admin authentication tests
│
├── integration/                         # Full-stack integration tests
│   ├── test_e2e_full_stack.py          # Complete end-to-end workflow
│   ├── test_phase2_integration.py
│   ├── test_dynamic_metar_generation.py
│   └── test_metar_pairs_comprehensive.py
│
├── external_apis/                       # External API client tests
│   ├── test_aviation_weather_client.py
│   ├── test_aviationweather_live_api.py
│   ├── test_openaip_integration.py
│   └── test_schema_discovery_poller.py
│
├── edge_cases/                          # Edge cases and specific features
│   ├── test_task_3_1_integration.py
│   ├── test_task_3_2_cloud_layers.py
│   ├── test_task_3_2_integration.py
│   ├── test_task_3_3_integration.py
│   ├── test_task_3_3_visibility_weather.py
│   ├── test_task_3_4_failure_categorization.py
│   └── test_task_3_5_extended_coverage.py
│
├── infrastructure/                      # Infrastructure and CI/CD tests
│   ├── test_smoke.py                   # Quick smoke tests
│   ├── test_security_comprehensive.py  # Security tests
│   ├── test_docker_schematron_container.py
│   ├── test_schematron_docker_validator.py
│   ├── test_xsd_validator.py
│   ├── test_schema_registry.py
│   ├── test_coverage_boost.py
│   ├── test_eval_endpoint_integration.py
│   ├── test_endpoint_extended_coverage.py
│   ├── test_webhooks_service.py
│   └── test_live_api_health.py
│
├── versions/                            # Version-specific tests
│   ├── test_version_detector.py
│   ├── test_version_migration.py
│   ├── test_version_switching.py
│   └── test_version_deprecation.py
│
└── docs/                                # Test documentation
    ├── README.md
    ├── COMPLETE_SUMMARY.md
    ├── IMPLEMENTATION_SUMMARY.md
    ├── PHASE2_SUMMARY.md
    ├── E2E_TEST_COVERAGE_REPORT.md
    ├── TEST_ERROR_FIXES.md
    └── TEST_ORGANIZATION.md (this file)
```

## Test Categories

### unit/ - Unit Tests

Fast, isolated tests of individual components (< 5 minutes total).

**What's tested:**

- Individual utility functions
- Service components in isolation
- Parser functions

**When to run:** Every commit, pre-push

### api/ - API Endpoint Tests (5 files)

Tests for FastAPI endpoints with mocked external services.

**Features tested:**

- HTTP endpoints (GET, POST, PUT, DELETE)
- Request/response validation
- Authentication & authorization
- Error handling
- CORS configuration

**Key files:**

- `test_api_comprehensive.py` - Router inclusion, app initialization
- `test_api_error_handling.py` - Error response formats
- `test_api_validation.py` - Input validation

### conversion/ - Conversion Tests (6 files)

Tests for METAR→IWXXM conversion utilities.

**Features tested:**

- Basic METAR text conversion
- Multiple file handling
- Round-trip XML validation
- Edge cases and error handling

**Key files:**

- `test_convert.py` - Basic conversion workflow
- `test_roundtrip.py` - XML serialization/deserialization
- `test_conversion_edge_cases.py` - Known failures and edge cases

### validation/ - Validation Tests (9 files)

Tests for XML and schema validation including XSD and Schematron.

**Features tested:**

- XSD schema validation
- Schematron rule validation
- Semantic validation rules
- Validation error reporting

**Key files:**

- `test_validation_service.py` - Core validation service
- `test_schematron_validation_suite.py` - Schematron rules
- `test_iwxxm_validation.py` - IWXXM-specific validation

### iwxxm/ - IWXXM & XML Tests (7 files)

Tests for IWXXM version handling and XML generation.

**Features tested:**

- IWXXM version compatibility
- XML namespace handling
- WMO canonical examples
- XML serialization

**Key files:**

- `test_xml_version_utils.py` - Version utilities
- `test_iwxxm_versions_rc.py` - Version support
- `test_wmo_canonical_examples.py` - WMO spec examples

### services/ - Data Service Tests (4 files)

Tests for backend services and data access.

**Features tested:**

- Airport data management
- Database operations
- Statistics collection
- Station sampling

### evaluation/ - Evaluation System Tests (5 files)

Tests for aviation weather evaluation and ICAO OPMET reporting.

**Features tested:**

- Evaluation job management
- ICAO OPMET reporting
- Admin authentication
- Report generation

**Key files:**

- `test_evaluation_endpoints_comprehensive.py` - All evaluation endpoints
- `test_icao_opmet_admin.py` - Admin authentication

### integration/ - Integration & E2E Tests (4 files)

Full-stack tests with real or mocked services.

**What's tested:**

- Complete workflows from input to output
- Multi-component interactions
- Error handling across layers

**Key files:**

- `test_e2e_full_stack.py` - Complete end-to-end workflow (1,506 lines)

### external_apis/ - External API Tests (4 files)

Tests for external API clients and services.

**Features tested:**

- Aviation Weather API calls
- OpenAIP integration
- Schema polling

**Note:** Use `-m "not live_api"` to skip real API calls

### edge_cases/ - Edge Cases (7 files)

Tests for specific features and known issues.

**Features tested:**

- Cloud layer handling
- Visibility/weather parsing
- Failure categorization
- Task-specific implementations

### infrastructure/ - Infrastructure Tests (11 files)

Infrastructure, CI/CD, and operational tests.

**Features tested:**

- Smoke tests for rapid CI/CD
- Security validations
- Docker container operations
- Schematron validation via Docker

**Key files:**

- `test_smoke.py` - Quick smoke tests (~30 seconds)
- `test_security_comprehensive.py` - Security checks

### versions/ - Version Tests (4 files)

Tests for IWXXM version switching and compatibility.

**Features tested:**

- Version detection
- Version migration
- Backward compatibility
- Deprecation handling

## Running Tests

### All tests

```bash
pytest
```

### By category

```bash
pytest tests/api/                    # API tests only
pytest tests/conversion/             # Conversion tests only
pytest tests/validation/             # Validation tests only
pytest tests/integration/            # Integration tests only
```

### By marker

```bash
pytest -m unit                       # Unit tests only
pytest -m integration                # Integration tests
pytest -m smoke                      # Quick smoke tests (~30 seconds)
pytest -m "not live_api"             # Skip live API tests
pytest -m "not slow"                 # Skip slow tests
```

### With coverage

```bash
pytest --cov=src --cov-report=html   # Generate HTML coverage report
pytest --cov=src --cov-report=term-missing
```

### Specific tests

```bash
pytest tests/api/test_api.py::TestHealthEndpoint
pytest tests/conversion/test_convert.py::test_convert_manual_text
pytest tests/smoke.py -v
```

### Watch mode (requires pytest-watch)

```bash
ptw tests/api/                       # Re-run on file changes
```

## Test Markers

Available pytest markers:

- **unit** - Unit tests (isolated, < 1 second)
- **integration** - Integration tests (mocked services)
- **e2e** - End-to-end tests (real services)
- **smoke** - Critical path smoke tests
- **live_api** - Tests requiring real API calls
- **slow** - Slow-running tests (> 10 seconds)
- **asyncio** - Async tests
- **edge_case** - Known failures and edge cases
- **iwxxm_2023_1** - IWXXM 2023-1 specific
- **iwxxm_2025_2** - IWXXM 2025-2 specific

## Fixtures

Global fixtures are defined in `test_fixtures.py` and automatically available to all tests:

- `client` - FastAPI TestClient
- `auth_headers` - Test authentication headers
- `sample_metar` - Sample METAR strings
- `sample_xml` - Sample IWXXM XML

## Adding New Tests

1. **Identify the category** - Determine which subdirectory best fits your test
2. **Create/modify test file** - Add tests to existing or new file in the subdirectory
3. **Use appropriate markers** - Decorate your tests with `@pytest.mark.*`
4. **Follow naming conventions** - Functions start with `test_`, classes with `Test`
5. **Add docstrings** - Describe what's being tested

Example:

```python
# tests/api/test_my_endpoint.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestMyEndpoint:
    """Test new endpoint functionality."""

    def test_basic_request(self, client):
        """Test basic request succeeds."""
        response = client.get('/api/v1/my-endpoint')
        assert response.status_code == 200
```

## Best Practices

1. **Keep tests focused** - One assertion per test when possible
2. **Use fixtures** - Avoid duplication with pytest fixtures
3. **Mock external services** - Use `unittest.mock` for external dependencies
4. **Parametrize tests** - Use `@pytest.mark.parametrize` for multiple inputs
5. **Clear naming** - Test names should describe what's being tested
6. **Fast tests** - Unit tests should run in < 1 second
7. **Group related tests** - Use test classes to organize related tests

## Maintenance

### Running specific test suite

```bash
# API tests only
pytest tests/api/ -v

# Get coverage for subdirectory
pytest tests/conversion/ --cov=src --cov-report=term-missing
```

### Finding slow tests

```bash
pytest --durations=10
```

### Finding tests without docstrings

```bash
pytest --collect-only -q | grep -E "test_.*$" | wc -l
```

## Documentation Files

Test documentation is located in `tests/docs/`:

- **README.md** - Main testing guide
- **COMPLETE_SUMMARY.md** - Comprehensive test coverage summary
- **IMPLEMENTATION_SUMMARY.md** - Implementation details
- **PHASE2_SUMMARY.md** - Phase 2 work summary
- **E2E_TEST_COVERAGE_REPORT.md** - E2E coverage analysis
- **TEST_ERROR_FIXES.md** - Known error fixes and workarounds
- **TEST_ORGANIZATION.md** - This file

## Statistics

- **Total test files:** 72
- **Total tests:** 1,090+
- **Test categories:** 12
- **Core domains:** API, Conversion, Validation, IWXXM, Services, Integration

## Recent Changes

This refactoring reorganized 72 test files from a flat structure into 12 logical subdirectories while maintaining:

- ✅ All 1,090+ tests discoverable
- ✅ Correct import resolution
- ✅ Pytest configuration compatibility
- ✅ CI/CD pipeline compatibility
- ✅ Full test coverage reporting
