# Backend Testing Guide

Comprehensive testing infrastructure for the METAR to IWXXM Backend API.

## Quick Start

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests
pytest -m smoke                   # Quick smoke tests (~30s)
pytest -m "not live_api"          # Skip live API tests
pytest -m "not slow"              # Skip slow tests

# Run specific test files
pytest tests/test_evaluation_endpoints_comprehensive.py
pytest tests/test_icao_opmet_admin.py
pytest tests/test_live_api_health.py
pytest tests/test_smoke.py

# With coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing
```

## Test Pyramid

Our testing strategy follows a test pyramid approach:

```
        /\
       /  \      Live API Health Checks (production monitoring)
      /____\
     /      \    E2E Tests (full stack with real services)
    /________\
   /          \  Integration Tests (mocked external dependencies)
  /____________\
 /______________\ Unit Tests (isolated component testing)
       |
    Smoke Tests (critical path validation)
```

## Test Categories

### 1. Unit Tests (`-m unit`)

Fast, isolated tests of individual components without external dependencies.

- **Location**: `tests/test_*.py`
- **Runtime**: < 5 minutes
- **When to run**: On every commit, pre-push
- **Coverage target**: > 90%

**Examples:**

- `test_conversion.py` - Conversion logic
- `test_validation_service.py` - Validation service
- `test_tac_parser.py` - TAC parsing

### 2. Integration Tests (`-m integration`)

Tests of API endpoints with mocked external services (database, auth, etc.).

- **Location**: `tests/test_api*.py`, `tests/test_*_router.py`
- **Runtime**: < 10 minutes
- **When to run**: On PR, before merge
- **Coverage target**: > 85%

**Key test files:**

- `test_evaluation_endpoints_comprehensive.py` - All evaluation endpoints
- `test_icao_opmet_admin.py` - ICAO OPMET statistics with admin auth
- `test_validation_router.py` - Validation endpoints
- `test_api_comprehensive.py` - Core API endpoints

**Features tested:**

- ✅ All HTTP endpoints
- ✅ Request/response validation
- ✅ Authentication & authorization
- ✅ Error handling
- ✅ Pagination
- ✅ Filtering

### 3. Smoke Tests (`-m smoke`)

Critical path validation for rapid CI/CD pipelines.

- **Location**: `tests/test_smoke.py`
- **Runtime**: ~30 seconds
- **When to run**: On every PR, pre-deployment
- **Coverage**: Critical happy path only

**What's tested:**

- ✅ Health check responds
- ✅ Authentication works
- ✅ Single METAR conversion
- ✅ Single validation request
- ✅ Evaluation job creation
- ✅ Public endpoints accessible
- ✅ Error handling basics

**Usage:**

```bash
# Run smoke tests only
pytest -m smoke

# Run as pre-deployment check
python tests/test_smoke.py
```

### 4. Live API Health Checks (`-m live_api`)

Tests against actual deployed API for production monitoring.

- **Location**: `tests/test_live_api_health.py`
- **Runtime**: < 2 minutes
- **When to run**: Continuously in production, post-deployment
- **Environment**: Requires `LIVE_API_URL` and `LIVE_API_TOKEN`

**Configuration:**

```bash
export LIVE_API_URL=https://api.example.com
export LIVE_API_TOKEN=your_jwt_token_here
export LIVE_API_TIMEOUT=30

pytest -m live_api
```

**Checks performed:**

- ✅ Health endpoints respond
- ✅ API is reachable
- ✅ Response times acceptable
- ✅ Authentication works
- ✅ Basic conversion works
- ✅ CORS headers present
- ✅ JSON responses valid

### 5. End-to-End Tests (`-m e2e`)

Full-stack tests with real database, auth service, and external APIs.

- **Location**: `tests/test_e2e_*.py` (TODO: implementation in progress)
- **Runtime**: < 15 minutes
- **When to run**: Pre-release, staging environment
- **Requirements**: Real services running

**Not yet implemented** - Coming in future updates.

### 6. Slow Tests (`-m slow`)

Long-running tests that can be skipped in fast CI runs.

- **Runtime**: > 30 seconds each
- **Examples**: Large batch processing, performance tests

**Usage:**

```bash
# Skip slow tests
pytest -m "not slow"

# Run only slow tests
pytest -m slow
```

## Test Markers Reference

| Marker         | Description               | Runtime  | Environment            |
| -------------- | ------------------------- | -------- | ---------------------- |
| `unit`         | Unit tests                | < 5 min  | No deps                |
| `integration`  | Integration tests         | < 10 min | Mocked services        |
| `smoke`        | Critical path smoke tests | ~30 sec  | Mocked services        |
| `live_api`     | Live API health checks    | < 2 min  | Deployed API required  |
| `e2e`          | End-to-end tests          | < 15 min | Real services required |
| `slow`         | Slow-running tests        | > 30 sec | Varies                 |
| `asyncio`      | Async tests               | -        | -                      |
| `edge_case`    | Known edge cases/failures | -        | -                      |
| `iwxxm_2023_1` | IWXXM 2023-1 specific     | -        | -                      |
| `iwxxm_2025_2` | IWXXM 2025-2 specific     | -        | -                      |

## Test Fixtures

Common fixtures are provided in `test_fixtures.py`:

### Authentication Fixtures

- `client` - TestClient with regular user auth
- `admin_client` - TestClient with admin auth
- `unauthenticated_client` - TestClient without auth
- `user_client` - Alias for client (clarity)

### Service Mock Fixtures

- `mock_supabase_client` - Mock database client
- `mock_statistics_service` - Mock statistics service
- `mock_aviation_weather_client` - Mock Aviation Weather API
- `mock_validation_orchestrator` - Mock validation orchestrator

### Data Fixtures

- `sample_metars` - Dictionary of sample METAR strings
- `sample_iwxxm` - Sample IWXXM XML document
- `sample_station_ids` - List of international airport codes

### Live API Fixtures

- `live_api_client` - httpx AsyncClient for live API testing
- `skip_if_no_live_api` - Skip test if no live API configured

### Example Usage

```python
def test_something(client, sample_metars):
    """Test using fixtures."""
    response = client.post(
        "/api/v1/convert",
        json={"manual_text": sample_metars["simple"]}
    )
    assert response.status_code == 200
```

## Writing New Tests

### Pattern: Integration Test

```python
"""Test description."""
import pytest
from fastapi.testclient import TestClient

def test_endpoint_success(client):
    """Test endpoint returns success."""
    response = client.post(
        "/api/v1/endpoint",
        json={"param": "value"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### Pattern: Live API Test

```python
"""Live API test."""
import pytest

@pytest.mark.live_api
@pytest.mark.asyncio
async def test_live_endpoint(live_api_client):
    """Test live API endpoint."""
    response = await live_api_client.get("/health")

    assert response.status_code == 200
```

### Pattern: Mocked Service

```python
"""Test with mocked service."""
from unittest.mock import AsyncMock, MagicMock

def test_with_mock(client, mock_supabase_client):
    """Test with mocked database."""
    mock_supabase_client.get.return_value = AsyncMock(
        json=MagicMock(return_value=[{"id": "123"}]),
        raise_for_status=MagicMock()
    )

    response = client.get("/api/v1/resource/123")
    assert response.status_code == 200
```

## Syntax Validation

**Always validate Python syntax before committing test files** to catch errors early.

### Quick Syntax Check

```bash
# Check single file
python3 -m py_compile tests/test_your_module.py

# Check all test files
find tests -name "*.py" -exec python3 -m py_compile {} \;

# Use project syntax checker (recommended)
python scripts/utilities/syntax_check.py tests/
```

### Common Syntax Errors to Watch For

1. **Missing underscores in test names**

   ```python
   # ❌ Wrong - space instead of underscore
   def test airport_region(self, client):
       pass

   # ✓ Correct
   def test_airport_region(self, client):
       pass
   ```

2. **Unclosed parentheses/brackets**

   ```python
   # ❌ Wrong - missing closing parenthesis
   result = function(
       arg1, arg2

   # ✓ Correct
   result = function(
       arg1, arg2
   )
   ```

3. **Missing colons**

   ```python
   # ❌ Wrong - missing colon
   def test_something(self)
       pass

   # ✓ Correct
   def test_something(self):
       pass
   ```

### Automated Workflow

Integrate syntax validation into your development workflow:

```bash
# 1. Write tests
vim tests/test_new_feature.py

# 2. Validate syntax
python scripts/utilities/syntax_check.py tests/test_new_feature.py

# 3. Run tests
pytest tests/test_new_feature.py

# 4. Check coverage
pytest tests/test_new_feature.py --cov=src
```

### IDE Configuration

Configure your IDE for real-time syntax validation:

- **VS Code**: Install Python extension, enable Pylint or Ruff linting
- **PyCharm**: Built-in syntax checking enabled by default
- **Vim/Neovim**: Use ALE or CoC with pyright/pylsp
- **Emacs**: Use flycheck with flycheck-python-pylint

## Test Coverage

### Current Coverage Status

Run coverage report:

```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Coverage Targets

- **Overall**: > 85%
- **Critical paths**: > 95%
- **New code**: 100%

### Coverage by Component

| Component            | Target | Status               |
| -------------------- | ------ | -------------------- |
| Conversion endpoints | 95%    | ✅                   |
| Validation endpoints | 95%    | ✅                   |
| Evaluation endpoints | 95%    | ✅ (new tests added) |
| ICAO OPMET endpoints | 90%    | ✅ (new tests added) |
| Services             | 85%    | ⚠️ In progress       |
| Utilities            | 90%    | ✅                   |

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest -m unit

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
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running smoke tests..."
pytest -m smoke --tb=short
if [ $? -ne 0 ]; then
    echo "Smoke tests failed. Commit aborted."
    exit 1
fi
```

## Troubleshooting

### Common Issues

#### Tests fail with authentication error

```
Solution: Ensure test fixtures override verify_supabase_token dependency
```

#### Live API tests timeout

```
Solution: Set LIVE_API_TIMEOUT=60 or skip with -m "not live_api"
```

#### Import errors in tests

```
Solution: Ensure PYTHONPATH includes src/ directory or use uv run pytest
```

#### Database connection errors

```
Solution: Check DATABASE_URL points to test database (must contain "test")
```

### Debug Mode

```bash
# Verbose output with full tracebacks
pytest -vv -s --tb=long

# Stop on first failure
pytest -x

# Run specific test
pytest tests/test_file.py::TestClass::test_method -v
```

## Performance Testing

### Benchmarking

```bash
# Time each test
pytest --durations=10

# Profile slow tests
pytest --profile
```

### Load Testing

Run concurrent requests:

```python
@pytest.mark.slow
async def test_concurrent_requests():
    """Test API handles concurrent load."""
    tasks = [make_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in results)
```

## Documentation

- [TESTING_STRATEGY.md](../../docs/TESTING_STRATEGY.md) - Overall testing strategy
- [DEVELOPMENT.md](../../docs/DEVELOPMENT.md) - Development workflow
- [API.md](../../docs/API.md) - API documentation

## Phase 2: Advanced Testing Infrastructure (✅ Complete)

### E2E Tests with Real Services

Full stack integration testing:

**File**: `test_e2e_full_stack.py` (30+ tests)

```bash
# Setup environment
export DATABASE_URL="postgresql+asyncpg://postgres:pass@localhost/test_db"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"
export E2E_TEST_EMAIL="test@example.com"
export E2E_TEST_PASSWORD="testpass"

# Run E2E tests
pytest tests/test_e2e_full_stack.py -v -m e2e
```

**Coverage**: Real database, Supabase auth, complete workflows, performance benchmarks

### Extended Endpoint Coverage

Edge cases and performance testing:

**File**: `test_endpoint_extended_coverage.py` (60+ tests)

```bash
# Run extended coverage
pytest tests/test_endpoint_extended_coverage.py -v

# Specific test classes
pytest tests/test_endpoint_extended_coverage.py::TestLargeBatchProcessing -v
pytest tests/test_endpoint_extended_coverage.py::TestConcurrentRequestHandling -v
```

**Coverage**: Large batches (100-1000+ METARs), concurrent requests, ZIP errors, validation combinations

### GitHub Actions Monitoring Workflows

**1. API Health Monitoring** (`.github/workflows/api-health-check.yml`)

- Runs every 15 minutes
- Tests live API health
- Auto-creates issues on failure
- Slack alerts

**2. Smoke Tests on Deploy** (`.github/workflows/smoke-tests-deploy.yml`)

- Runs after deployment
- Multi-environment support
- Rollback decision workflow

**3. E2E Tests** (`.github/workflows/e2e-tests.yml`)

- Daily at 2 AM UTC
- PostgreSQL + Supabase
- Performance benchmarks

### Monitoring Dashboard

Grafana dashboard configuration: `monitoring/grafana-dashboard.json`

**Panels**: Health status, uptime, request rate, response time, error rate, conversion success, active jobs, database connections, regional stats, alerts

## Contributing

When adding new endpoints:

1. ✅ Write integration tests first (TDD)
2. ✅ Add to smoke tests if critical path
3. ✅ Update this README with new test files
4. ✅ Ensure > 90% coverage for new code
5. ✅ Add live API health check if user-facing

## Questions?

- Check existing tests for patterns
- Review test fixtures in `test_fixtures.py`
- See [TESTING_STRATEGY.md](../../docs/TESTING_STRATEGY.md)
