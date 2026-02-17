# Backend Test Coverage Standards

## Overview

This document outlines the test coverage requirements and standards for the METAR to IWXXM Backend API. All code must meet minimum coverage thresholds to ensure quality and maintainability.

## Coverage Requirements

### Minimum Thresholds

- **Overall Project**: 90% minimum coverage
- **API Endpoints** (`src/api.py`): 95% minimum coverage  
- **Schemas** (`src/schemas/`): 100% required (all data models)
- **Utilities** (`src/utilities/`): 90% minimum coverage
- **Services** (`src/services/`): 85% minimum coverage

### Current Status

| Module | Current | Target | Status |
|--------|---------|--------|--------|
| `src/schemas/` | 100% | 100% | ✅ PASSING |
| `src/api.py` | 79% | 95% | 🔄 IN PROGRESS |
| `src/utilities/conversion.py` | 33% | 90% | ⚠️ NEEDS WORK |
| `src/utilities/security.py` | 27% | 90% | ⚠️ NEEDS WORK |
| **Overall** | 58% | 90% | ⚠️ NEEDS WORK |

**Test Execution Status** (Last run - Feb 2025):
```
✅ 32 PASSED (API, Schemas, Utilities)
⏭️ 144 SKIPPED (GIFTs namespace mismatch - see KNOWN_ISSUES.md)
📊 Coverage: 58% (310 total statements, 161 covered)
⏱️ Time: 2.26s total
```

**Breakdown by Module**:
- ✅ test_api.py: 10/10 PASSED (Health, Convert, Convert-ZIP, Error handling)
- ✅ test_schemas.py: 13/13 PASSED (All Pydantic models)
- ✅ test_utilities_conversion.py: 9/9 PASSED (METAR/SPECI conversion)
- ⏭️ test_iwxxm_examples.py: 109 SKIPPED (IWXXM 2025-2 vs 2023-1 namespace)
- ⏭️ test_roundtrip.py: 34 SKIPPED (Same namespace version mismatch)

**Note**: For details on the skipped tests and namespace version mismatch issue, see [backend/KNOWN_ISSUES.md](KNOWN_ISSUES.md).

## CI/CD Enforcement

### GitHub Actions Workflow

The `.github/workflows/ci-cd.yml` workflow enforces coverage requirements:

1. **Unit Tests Job**
   - Runs on every push to `main`, `dev` branches and PRs
   - Fails if coverage drops below 90%
   - Uploads coverage to Codecov
   - Generates HTML report

2. **Coverage Tracking Job**
   - Prevents regression by comparing to baseline
   - Fails if coverage drops from established baseline
   - Auto-updates baseline on main branch

3. **Blocking Merges**
   - PRs cannot merge unless all tests pass
   - Coverage violations block PR approval
   - Status checks required before merge

### Local Testing

You must ensure tests pass locally before pushing:

```bash
# Run all tests with coverage
cd backend
python3 -m pytest tests/ -v --cov=src --cov-fail-under=90

# View coverage report in browser
open htmlcov/index.html
```

## Test Organization

### Unit Tests

Located in `backend/tests/`:

```
backend/tests/
├── test_api.py              # API endpoint tests
├── test_schemas.py          # Data model validation
├── test_utilities_*.py      # Utility function tests
└── conftest.py              # Shared fixtures
```

### Test Markers

Tests are marked for classification:

```python
import pytest

@pytest.mark.unit
def test_something_fast():
    """Fast unit test - 100ms"""
    pass

@pytest.mark.integration  
def test_something_slow():
    """Integration test - may be slower"""
    pass

@pytest.mark.e2e
def test_full_workflow():
    """End-to-end test"""
    pass
```

Run specific test categories:

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# E2E tests only
pytest tests/ -m e2e

# All except E2E
pytest tests/ -m "not e2e"
```

## Adding Tests

### Template for New Tests

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

class TestNewFeature:
    """Test suite for new feature."""
    
    def test_happy_path(self, client):
        """Test normal operation."""
        result = do_something()
        assert result is not None
        
    def test_error_case(self, client):
        """Test error handling."""
        with pytest.raises(ValueError):
            do_something_invalid()
            
    def test_edge_case(self, client):
        """Test boundary conditions."""
        result = do_something(edge_value)
        assert result == expected
```

### Mocking External Dependencies

```python
# For authentication
from utilities.security import verify_supabase_token

@pytest.fixture
def auth_override():
    async def override_auth():
        return {"sub": "test-user", "aud": "test"}
    
    app.dependency_overrides[verify_supabase_token] = override_auth
    yield
    app.dependency_overrides.clear()

# For HTTP calls
@patch('httpx.AsyncClient.get')
def test_with_http_mock(mock_get):
    mock_get.return_value.json.return_value = {"data": "value"}
    # ... test code
```

## Coverage Analysis

### Identifying Uncovered Lines

HTML reports show exactly which lines lack coverage:

```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

### JSON Report for CI/CD

Coverage is stored in `coverage.json` for tracking:

```json
{
  "percent": 48.06,
  "lines_total": 274,
  "lines_covered": 132,
  "timestamp": "2026-02-04T00:00:00Z"
}
```

## Pre-Commit Checks

Before committing code:

```bash
# Run tests locally
cd backend && python3 -m pytest tests/ -v --cov=src --cov-fail-under=90

# Check coverage report
cat coverage.json | jq .percent  # Should show >= 90

# If coverage is low, write more tests!
# - Add tests for error paths
# - Add edge case tests  
# - Add integration tests
```

## Priority Coverage Areas (For Expansion to 90%)

### High Priority (Currently <40%)

1. **`src/utilities/security.py` (27%)**
   - JWT token verification
   - JWKS caching logic
   - Invalid token handling
   - Token expiry validation
   - Authorization errors

   Example tests needed:
   ```python
   def test_valid_jwt_token():
       """Verify valid token passes verification"""
       
   def test_expired_jwt_token():
       """Expired token should raise error"""
       
   def test_invalid_signature():
       """Invalid signature should be rejected"""
   ```

2. **`src/utilities/conversion.py` (33%)**
   - Aerodrome metadata lookup
   - Error path handling
   - TAC parsing edge cases
   - XML output validation
   - Malformed input handling

   Example tests needed:
   ```python
   def test_metar_with_invalid_station():
       """Handle unknown station codes"""
       
   def test_missing_required_fields():
       """Require METAR format compliance"""
       
   def test_xml_well_formedness():
       """Verify output XML is valid"""
   ```

### Medium Priority (40-80%)

3. **`src/api.py` (79%)**
   - Error responses with invalid auth
   - Concurrent request handling
   - Large file handling  
   - Rate limiting scenarios
   - CORS validation

### Must Have Coverage

- All error paths must be tested
- All API response codes must be tested (200, 400, 403, 500, etc.)
- All schema models must validate both valid and invalid inputs
- All external service calls must be mocked and tested

## Regression Prevention

### Baseline Tracking

Coverage baseline is stored in `.coverage-baseline.json`:

```json
{
  "percent": 48.06,
  "lines_total": 274,
  "lines_covered": 132,
  "timestamp": "2026-02-04T00:00:00Z",
  "note": "Current baseline from 22 passing unit tests"
}
```

**Workflow**:
1. Local tests run and measure coverage
2. GitHub Actions workflow compares to baseline
3. If coverage drops, workflow fails
4. If coverage improves, baseline auto-updates on main branch

### Protecting Against Regression

Cannot merge PRs that:
- Reduce coverage percentage
- Add untested code paths
- Remove existing tests

## Tools & Commands

### Pytest Configuration

All pytest configuration is in `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]
addopts = [
    "-v",
    "--cov=src",
    "--cov=utilities", 
    "--cov=services",
    "--cov=schemas",
    "--cov-report=term-missing",
    "--cov-report=json",
    "--cov-report=html",
    "--tb=short",
]
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "e2e: end-to-end tests",
]
```

### Common Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestHealthEndpoint

# Run specific test method
pytest tests/test_api.py::TestHealthEndpoint::test_health_status_succeeds

# Show missing lines
pytest --cov-report=term-missing

# Generate HTML report
pytest --cov-report=html

# Quick test (no coverage)
pytest --no-cov

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Parallel execution (need pytest-xdist)
pytest -n auto
```

## Best Practices

### DO

✅ Write tests BEFORE writing feature code (TDD)  
✅ Test error cases and edge cases, not just happy path  
✅ Mock external dependencies (auth, HTTP, databases)  
✅ Use fixtures for common setup  
✅ Keep test names descriptive (`test_invalid_token_raises_error`)  
✅ Test response contracts (schema validation)  
✅ Use parametrized tests for multiple cases  
✅ Ensure tests are independent and idempotent  

### DON'T

❌ Skip error path testing  
❌ Leave untested code in pull requests  
❌ Comment out tests instead of fixing them  
❌ Create flaky tests that fail intermittently  
❌ Test implementation details (test behavior instead)  
❌ Violate the 90% coverage requirement  
❌ Merge PRs with failing tests  

## References

- [pytest documentation](https://docs.pytest.org/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
