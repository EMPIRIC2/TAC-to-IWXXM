# Backend Repository Structure

## Overview

The backend is organized into logical subdirectories for better maintainability and clarity:

```
backend/
├── src/                 # Source code
│   ├── api/            # FastAPI application
│   ├── utilities/      # Shared utilities (conversion, validation, etc.)
│   ├── services/       # Business logic services
│   ├── schemas/        # Data validation schemas
│   ├── clients/        # External API clients
│   ├── routers/        # API route handlers
│   ├── models/         # Data models
│   ├── config/         # Configuration
│   └── validation/     # Validation rules
│
├── tests/              # Test suite (1,090+ tests organized by category)
│   ├── api/           # API endpoint tests
│   ├── conversion/     # Conversion tests
│   ├── validation/     # Validation tests
│   ├── iwxxm/         # IWXXM and XML tests
│   ├── services/      # Service tests
│   ├── evaluation/    # Evaluation system tests
│   ├── integration/   # End-to-end tests
│   ├── external_apis/ # External API client tests
│   ├── edge_cases/    # Feature-specific tests
│   ├── infrastructure/# Infrastructure tests
│   ├── versions/      # Version compatibility tests
│   ├── unit/          # Unit tests
│   ├── docs/          # Test documentation
│   └── [utilities]    # Shared test utilities
│
├── docker/            # Docker configuration
│   ├── Dockerfile          # Main application container
│   └── Dockerfile.schematron  # Schematron validation container
│
├── scripts/           # Utility and maintenance scripts
│   ├── README.md
│   ├── analyze_version_comparisons.py
│   ├── compare_iwxxm_versions.sh
│   ├── fetch_openaip_airports.py
│   ├── generate_test_data.py
│   ├── mirror_wmo_bundles.py
│   ├── start_dev.sh
│   ├── test_sprint1_data_integration.py
│   ├── update_airports_db.py
│   └── validate_generated_xml_schematron.py
│
├── schemas/           # Schema files (IWXXM, etc.)
├── test-data/         # Test data files
├── test-reports/      # Generated test reports
│
├── .archive/          # Archived/deprecated files
│   ├── conversion.py.bak
│   └── schematron_validator.py.bak
│
├── conftest.py        # Pytest root configuration
├── pyproject.toml     # Project configuration (dependencies, metadata)
├── README.md          # Main project README
├── .env               # Environment variables (local)
├── uv.lock            # Dependency lock file
├── htmlcov/           # Code coverage reports (generated)
│
└── [system]
    ├── __pycache__/   # Python cache
    └── .pytest_cache/ # Pytest cache
```

## Directory Purposes

### src/

Main Python application source code, including utilities, services, API routes, and business logic.

**Key files:**

- `api.py` - FastAPI application
- `utilities/conversion.py` - METAR→IWXXM conversion
- `utilities/schematron_validator.py` - XML validation
- `services/` - Business logic (evaluation, validation orchestration, etc.)
- `clients/` - External API clients (aviation weather, OpenAIP, etc.)

### tests/

Comprehensive test suite with 1,090+ tests organized by functionality:

- API endpoint tests
- Conversion logic tests
- Validation tests
- IWXXM compatibility tests
- Full E2E integration tests

See [tests/README.md](tests/README.md) and [tests/docs/TEST_ORGANIZATION.md](tests/docs/TEST_ORGANIZATION.md) for details.

### docker/

Docker container definitions:

- `Dockerfile` - Main application container
- `Dockerfile.schematron` - Schematron validator container

Build with:

```bash
docker build -f docker/Dockerfile -t metar-backend .
docker build -f docker/Dockerfile.schematron -t metar-schematron .
```

### scripts/

Utility scripts for development and maintenance:

- `start_dev.sh` - Start development server
- `mirror_wmo_bundles.py` - Mirror WMO schema bundles
- `validate_generated_xml_schematron.py` - Validate generated XML
- `generate_test_data.py` - Generate test data
- `update_airports_db.py` - Update airport database
- `fetch_openaip_airports.py` - Fetch OpenAIP airport data
- `analyze_version_comparisons.py` - Analyze version differences
- `compare_iwxxm_versions.sh` - Compare IWXXM versions

See [scripts/README.md](scripts/README.md) for details.

### schemas/

IWXXM and data schemas for validation and code generation.

### test-data/

Sample METAR strings, XML documents, and other test data files.

### .archive/

Deprecated or backup files:

- `conversion.py.bak` - Older conversion wrapper (use src/utilities/conversion.py)
- `schematron_validator.py.bak` - Older validator (use src/utilities/schematron_validator.py)

## Configuration Files

### pyproject.toml

Project metadata, dependencies, and tool configuration:

- Dependencies (fastapi, uvicorn, lxml, httpx, etc.)
- Dev dependencies (pytest, pytest-cov, pytest-asyncio, etc.)
- Pytest configuration
- Entry points

### conftest.py

Pytest configuration at root level for global fixtures and configuration.
Also configure test discovery and markers.

### .env

Environment variables for local development:

```
DATABASE_URL=...
SUPABASE_URL=...
SUPABASE_KEY=...
DISABLE_AUTH=false
```

### uv.lock

Locked dependency versions for reproducible builds (managed by `uv` package manager).

## Quick Commands

### Development

```bash
# Start development server
./scripts/start_dev.sh

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test category
pytest tests/api/
pytest tests/conversion/
```

### Docker

```bash
# Build main container
docker build -f docker/Dockerfile -t metar-backend .

# Build schematron container
docker build -f docker/Dockerfile.schematron -t metar-schematron .

# Run with docker-compose
docker-compose up -d
```

### Data & Utilities

```bash
# Mirror WMO bundles
python scripts/mirror_wmo_bundles.py

# Validate generated XML
python scripts/validate_generated_xml_schematron.py <xml_file>

# Update airports
python scripts/update_airports_db.py

# Generate test data
python scripts/generate_test_data.py
```

## Import Paths

### From tests

```python
# Import from src utilities
from src.utilities.conversion import convert_metar_tac
from src.utilities.schematron_validator import validate_schematron

# Import from src services
from src.services.evaluation import EvaluationService
from src.services.validation import ValidationService
```

### From application

```python
# Within src/
from utilities.conversion import convert_metar_tac
from services.validation import ValidationService
```

## Adding New Code

1. **Utilities** → `src/utilities/`
2. **Services** → `src/services/`
3. **API Routes** → `src/routers/`
4. **Models** → `src/models.py`
5. **Tests** → `tests/[category]/`
6. **Scripts** → `scripts/`

## CI/CD Integration

Project uses organized test structure for CI/CD:

- **Smoke tests** → `pytest -m smoke` (~30 seconds)
- **Unit tests** → `pytest tests/unit/`
- **API tests** → `pytest tests/api/`
- **Integration tests** → `pytest tests/integration/`
- **All tests** → `pytest tests/`

## Archived Files

The `.archive/` directory contains deprecated files:

- `conversion.py.bak` - Use `src/utilities/conversion.py` instead
- `schematron_validator.py.bak` - Use `src/utilities/schematron_validator.py` instead

These files are kept as reference but should not be used.

## Recent Changes

- ✅ Moved Dockerfiles to `docker/`
- ✅ Moved utility scripts to `scripts/`
- ✅ Reorganized tests into 12 categories
- ✅ Archived deprecated root-level files
- ✅ Created comprehensive documentation

---

**Structure Updated:** February 17, 2026  
**Status:** Production Ready ✅
