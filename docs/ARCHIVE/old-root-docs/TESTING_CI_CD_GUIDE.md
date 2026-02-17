# Test Suite & CI/CD Pipeline Documentation

## Overview

This document describes the comprehensive testing and CI/CD infrastructure set up for the METAR to IWXXM Backend API.

## Testing Structure

### Unit Tests
Located in `backend/tests/`:
- **test_api.py**: Full API endpoint testing with mocked authentication
  - Health check endpoint
  - Single and batch conversion endpoints
  - ZIP file generation
  - Error handling
- **test_schemas.py**: Pydantic model validation
  - All response schemas
  - Validation rules
  - JSON serialization
- **test_utilities_conversion.py**: Conversion utility functions
  - METAR/SPECI TAC parsing and conversion
  - Error handling for invalid input
  - Multiple conversion chains

### Integration Tests
Located in `tests/`:
- **test_integration.py**: Cross-service integration tests
  - End-to-end workflows
  - API integration with backend services
  - Health check with actual conversion
  - Error handling across API

### Current Coverage
- **Overall**: 48%+ (in initial state)
- **api.py**: 79% coverage  
- **schemas**: 100% coverage
- **utilities**: 33% coverage (conversion logic)

## GitHub Actions Workflow

### CI/CD Pipeline: `.github/workflows/ci-cd.yml`

The workflow runs on push to `main` and `dev` branches, plus all PRs.

#### Jobs:

1. **unit-tests** (Runs Always)
   - Python 3.11 environment
   - Installs backend dependencies
   - Runs pytest with coverage reporting
   - Uploads coverage to Codecov
   - Checks coverage is >= 90%
   - Artifacts: HTML coverage report

2. **integration-tests** (Depends: unit-tests)
   - Runs integration and E2E tests
   - Coverage reporting
   - Continues on error to not block deployment

3. **build-and-push** (Depends: unit+integration, Main/Dev branches only)
   - Builds Docker image from `backend/Dockerfile`
   - Pushes to GitHub Container Registry (ghcr.io)
   - Tags with: branch, semver, SHA, latest (for main)
   - Uses buildcache for faster builds

4. **coverage-tracking** (Depends: unit-tests)
   - Compares current vs baseline coverage
   - Prevents regression (fails if coverage drops)
   - Updates baseline on main branch only
   - Maintains `.coverage-baseline.json`

5. **test-summary** (Final job)
   - Generates summary table in PR/commit checks
   - Shows status of all previous jobs

## Configuration Files

### pytest.ini
```ini
[pytest]
testpaths = tests backend/tests
pythonpath = backend/src:.
addopts = 
    -v
    --cov=src
    --cov=utilities
    --cov=services
    --cov=schemas
    --cov-report=term-missing
    --cov-report=json
    --cov-report=html
    --tb=short
```

### conftest.py
- Shared pytest configuration
- Path setup for backend imports
- Pytest marker definitions (unit, integration, e2e)

### .coverage-baseline.json
- Tracks minimum acceptable coverage
- Updated automatically on main branch
- Prevents regression in coverage percentage

## Running Tests Locally

### Run All Unit Tests
```bash
cd /root/metar-to-IWXXM/backend
python3 -m pytest tests/ -v --cov=src --cov-report=html
```

### Run Specific Test Class
```bash
python3 -m pytest tests/test_api.py::TestHealthEndpoint -v
```

### Run with Coverage Minimum Check
```bash
python3 -m pytest --cov=src --cov-fail-under=90
```

### Generate HTML Report
```bash
python3 -m pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Run Integration Tests
```bash
cd /root/metar-to-IWXXM
python3 -m pytest tests/test_integration.py -v -m integration
```

## Coverage Regression Prevention

### How It Works:
1. **First Run**: Baseline set to 0%
2. **Main Branch**: Baseline updated with each successful push
3. **PRs**: Coverage must not drop below baseline
4. **Reporting**: GitHub Actions shows coverage % in workflow summary

### Workflow Permissions:
- Checks out `coverage-baseline` branch
- Compares current vs stored baseline
- Auto-commits baseline updates to special branch
- Prevents direct commits to main coverage

## Docker Build & Registry

### Image Details:
- **Registry**: ghcr.io (GitHub Container Registry)
- **Image Name**: `github.com/<owner>/metar-to-iwxxm/backend`
- **Tags**:
  - Branch name (dev, main)
  - Git SHA (for traceability)
  - Semantic versions (if tagged)
  - `latest` (for main branch only)

### Access:
```bash
docker login ghcr.io
docker pull ghcr.io/github.com/<owner>/metar-to-iwxxm/backend:main
```

## Authentication for Docker Registry

Uses GitHub token automatically in Actions:
- `${{ secrets.GITHUB_TOKEN }}`
- Pre-authenticated via `docker/login-action@v2`
- Personal Access Token can be used for manual pulls

## Adding New Tests

### Unit Test Template:
```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    async def override_auth():
        return {"sub": "test-user", "aud": "test"}
    app.dependency_overrides[verify_supabase_token] = override_auth
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_new_feature(client):
    r = client.post("/api/endpoint", data={"input": "value"})
    assert r.status_code == 200
```

### Integration Test Template:
```python
@pytest.mark.integration
def test_e2e_workflow(client):
    # Test across multiple endpoints/services
    pass
```

### Marking Tests:
```python
@pytest.mark.unit
def test_something(): pass

@pytest.mark.integration  
def test_something_else(): pass

@pytest.mark.e2e
def test_full_workflow(): pass
```

## Next Steps for 90%+ Coverage

To reach 90% coverage, add tests for:
1. **utilities/security.py** (27% → 100%)
   - JWT token verification
   - JWKS caching logic
   - Error cases
2. **utilities/conversion.py** (33% → 100%)
   - Aerodrome database lookup
   - Error paths
   - Metadata enrichment
3. **API edge cases** (79% → 100%)
   - File content-type validation
   - Large file handling
   - Concurrent requests
4. **services/** (0% → 100%)
   - Business logic layer
   - Service methods

## Deployment Flow

```
Code Push
    ↓
GitHub Actions
    ├─ Unit Tests (must pass)
    ├─ Integration Tests (runs after unit)
    ├─ Coverage Check (90% minimum)
    ├─ Regression Check (vs baseline)
    ├─ Build Docker Image
    └─ Push to ghcr.io
    ↓
Docker Image Ready for Deployment
```

## Monitoring & Alerts

- **PR Status Checks**: Show test results
- **Codecov Integration**: Upload coverage data
- **Workflow Summary**: In PR checks section
- **Failed Builds**: Block merge if tests fail

## Files Modified/Created

- `.github/workflows/ci-cd.yml` - Main CI/CD workflow
- `pytest.ini` - Pytest configuration
- `conftest.py` - Shared test fixtures
- `.coverage-baseline.json` - Coverage baseline tracking
- `backend/tests/test_api.py` - Enhanced API tests (22 tests)
- `backend/tests/test_schemas.py` - Schema validation tests (13 tests)
- `backend/tests/test_utilities_conversion.py` - Utilities tests (9 tests)
- `tests/test_integration.py` - Integration/E2E tests (6 tests)

## References

- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Codecov Integration](https://codecov.io/gh)
