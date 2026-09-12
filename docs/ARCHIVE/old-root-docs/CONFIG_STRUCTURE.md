# Repository Configuration Structure

This document explains how the metar-to-IWXXM repository is organized with respect to build, test, and package configuration files.

## Philosophy

Each subdirectory (backend, frontend, auth) is designed to be **independent** with respect to its build and test environment:

- **Root-level config**: Only for items that apply to ALL subdirectories (none currently)
- **Subdirectory config**: Each directory manages its own build, tests, and dependencies
- **Dependencies**: Frontend depends on backend; tests repo depends on all others

## Current Structure

```
/root/metar-to-IWXXM/
├── backend/
│   ├── pytest.ini              ← Backend-specific pytest configuration
│   ├── conftest.py             ← Backend test fixtures
│   ├── pyproject.toml          ← Python package definition
│   ├── tests/                  ← Backend test suite
│   └── src/                    ← Source code
│
├── frontend/
│   ├── package.json            ← Node.js package definition
│   ├── playwright.config.ts    ← Frontend test configuration
│   └── tests/                  ← Frontend test suite
│
├── auth/
│   ├── pytest.ini              ← Auth-specific pytest configuration
│   ├── pyproject.toml          ← Python package definition
│   ├── tests/                  ← Auth test suite
│   └── src/                    ← Source code
│
└── data/                       ← Shared test data (IWXXM amendments)
```

## Configuration Files

### Backend (`backend/pytest.ini`)

```ini
[pytest]
testpaths = tests
pythonpath = src:.
addopts = -v --cov=src --cov-report=term-missing
```

**Features**:
- Only runs tests in `backend/tests/`
- Only covers code in `backend/src/`
- Omits untested `src/services/` module
- Automatically finds fixtures in `backend/conftest.py`

### Backend (`backend/conftest.py`)

Sets up Python path for backend-specific tests:
- Adds `backend/src/` to `sys.path`
- No root-level paths needed

### Root Directory

**No configuration files** - eliminates conflicts between:
- Backend pytest vs auth pytest vs frontend Jest
- Different Python versions/packages per subdirectory
- Cross-workspace interference

## Running Tests

### Backend Only

```bash
cd backend
pytest tests/
# Uses backend/pytest.ini + backend/conftest.py
```

### Frontend Only

```bash
cd frontend
npm test
# Uses playwright.config.ts
```

### Auth Only

```bash
cd auth
pytest tests/
# Uses auth/pytest.ini + auth/conftest.py
```

### All (Future)

When integrating multiple test suites, create a `Makefile` or CI pipeline that runs each independently:

```bash
make test  # Runs backend/tests + frontend/tests + auth/tests
```

## IWXXM Test Data

Located in `data/iwxxm-translation/` (shared):

- **Amd77-2016** - IWXXM 2016-1 format
- **Amd78-2018** - IWXXM 3.0 and 2018-2 formats
- **Amd79-80-2021** - IWXXM 2021-2 format
- **Amd79-80-2023** - IWXXM 2023-1 format

Tests access data using relative paths: `data/iwxxm-translation/Amd*/metar/`

## Configuration Details

### Backend pytest.ini

```ini
[pytest]
testpaths = tests                    # Only backend/tests/
pythonpath = src:.                   # Backend-relative paths
addopts = 
    -v                               # Verbose
    --cov=src                        # Coverage for src/
    --cov-report=term-missing        # Show missing lines
    --cov-report=json
    --cov-report=html
    --tb=short                       # Short tracebacks
python_files = test_*.py             # Standard naming
python_classes = Test*
python_functions = test_*
markers =
    integration: Integration tests
    e2e: End-to-end tests
    unit: Unit tests

[coverage:run]
omit = src/services/*                # Skip untested services
```

### Backend conftest.py

```python
import pathlib
import sys

# Backend-specific setup
BACKEND_DIR = pathlib.Path(__file__).resolve().parent
BACKEND_SRC = BACKEND_DIR / "src"

if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))
```

**Key difference from root-level conftest:**
- Resolves paths relative to `backend/` (where it lives)
- Not relative to repository root
- No cross-directory interference

## Adding New Test Suites

When adding tests to another service:

1. **Create `new-service/pytest.ini`** with:
   - `testpaths = tests` (relative to new-service/)
   - `pythonpath = src:.` (relative to new-service/)

2. **Create `new-service/conftest.py`** with:
   - Path resolution relative to new-service/
   - Service-specific fixtures only

3. **Do NOT modify root-level config** - keep it empty

4. **Update root Makefile** to run: `cd new-service && pytest`

## CI/CD Implications

Each subdirectory can have independent CI/CD:

```yaml
backend/.github/workflows/test.yml
- Runs: cd backend && pytest
- Caches: Python dependencies only
- Artifacts: coverage reports

frontend/.github/workflows/test.yml
- Runs: cd frontend && npm test
- Caches: Node modules only
- Artifacts: test reports

auth/.github/workflows/test.yml
- Runs: cd auth && pytest
- Caches: Python dependencies only
```

## Summary

✅ **Each subdirectory manages its own:**
- Test configuration (pytest.ini)
- Fixtures (conftest.py)
- Dependencies (pyproject.toml / package.json)
- Caching and CI/CD

✅ **Root directory:**
- Empty of test/build config
- Contains only README, LICENSE, shared data

✅ **Benefits:**
- No cross-workspace conflicts
- Easy to move services to separate repos
- Clear dependency flow (Frontend→Backend→Auth)
- Scalable to many services
