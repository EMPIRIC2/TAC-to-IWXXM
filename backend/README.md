# Backend: METAR to IWXXM Conversion API

## Overview

FastAPI-based REST API for converting METAR (Aerodrome Routine Weather Report) and SPECI (Aviation Selected Special Weather Report) aviation weather observations into IWXXM (ICAO Meteorological Information Exchange Model) XML format.

**Status**: ✅ 230 tests passing (65% coverage), 1 intentionally skipped

## Quick Start

```bash
cd backend

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run server (development)
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8001

# Run server (production)
gunicorn src.api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

Server runs on `http://localhost:8001`
- API Docs: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- Health: http://localhost:8001/health

## Architecture

### Directory Structure

```
backend/
├── src/
│   ├── __main__.py                      # Entry point
│   ├── api.py                           # FastAPI app (79% coverage)
│   ├── schemas/
│   │   ├── conversion.py                # Pydantic models (100%)
│   │   └── iwxxm_validation.py          # IWXXM validation (92%)
│   ├── utilities/
│   │   ├── conversion.py                # TAC→IWXXM (65%)
│   │   └── security.py                  # Auth (27%)
│   └── services/                        # Placeholder (0%)
├── tests/                               # 230 passing tests
├── pyproject.toml                       # Package + pytest config
├── pytest.ini                           # Pytest config (legacy)
└── README.md                            # This file
```

### Coverage Summary

```
Module                                  Stmts  Miss  Cover
─────────────────────────────────────────────────────────
src/schemas/conversion.py                 23    0   100% ✅
src/schemas/__init__.py                    2    0   100% ✅
src/utilities/__init__.py                  3    0   100% ✅
src/schemas/iwxxm_validation.py           76    6    92% ✅
src/api.py                                92   19    79% 🟡
src/utilities/conversion.py               98   34    65% 🟡
src/utilities/security.py                 59   43    27% 🔴
src/__main__.py                           17   17     0% 🔴
src/backend/__init__.py                    2    2     0% 🔴
─────────────────────────────────────────────────────────
TOTAL                                   386  135    65%
```

**Target: 90% coverage** (need ~80 more statements covered)

## IWXXM Support

### Supported Versions

- ✅ **2016-1** (Amd77) - XML files only
- ✅ **3.0** (Amd78 variant) - 38 METAR examples
- ✅ **2018-2** (Amd78) - 38 METAR examples
- ✅ **2021-2** (Amd79-80) - 37 METAR examples
- ✅ **2023-1** (Amd79-80) - 34 METAR examples
- ✅ **2025-2** (GIFTs output) - Generated dynamically

### Test Data

Located in `data/iwxxm-translation/`:

| Amendment | Version | METAR | Status |
|-----------|---------|-------|--------|
| Amd77-2016 | 2016-1 | — | XML files only |
| Amd78-2018 | 3.0/2018-2 | 38 ✅ | Full TAC→XML |
| Amd79-80-2021 | 2021-2 | 37 ✅ | Full TAC→XML |
| Amd79-80-2023 | 2023-1 | 34 ✅ | Full TAC→XML |

**Note**: Test data is 2023-1 (input) but GIFTs produces 2025-2 (output). Tests validate both formats.

## Test Execution

```bash
# Run all tests
pytest tests/

# Verbose with coverage
pytest tests/ -v --cov-report=html

# Specific test file
pytest tests/test_api.py -v

# Specific marker
pytest tests/ -m unit -v

# With coverage report
pytest tests/ --cov --cov-report=term-missing
```

### Test Breakdown: 230 Passing

| Category | Tests | Focus |
|----------|-------|-------|
| API Endpoints | 10 | Health, convert, errors |
| Schema Validation | 13 | Pydantic models, serialization |
| IWXXM Examples | 109 | Version-specific conversions |
| Roundtrip Pipeline | 68 | GIFTs decoder→encoder |
| Metadata Validation | 21 | Features, volcanic, nil-reason |
| Utilities | 9 | Conversion functions |
| **Total** | **230** | 100% passing ✅ |
| Skipped | 1 | XML→TAC (not implemented) |

## Configuration

### pyproject.toml

Includes pytest configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]
addopts = [
    "-v",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]

[tool.coverage.run]
omit = ["src/services/*"]  # Skip untested infrastructure
```

### Environment Variables

```bash
# Server config
HOST=0.0.0.0
PORT=8001
WORKERS=4

# Frontend integration
FRONTEND_URL=http://localhost:3000

# Authentication (optional)
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2024-02-04T..."
}
```

### Convert Single METAR

```bash
curl -X POST http://localhost:8001/convert \
  -H "Content-Type: application/json" \
  -d '{"tac": "METAR KJFK 121251Z 24008KT 10SM FEW250 M04/M17 A3034 RMK AO2 SLP279 T10441172"}'
```

Response:
```json
{
  "success": true,
  "data": {
    "xml": "<iwxxm:METAR xmlns:iwxxm=\"http://icao.int/iwxxm/2025-2\">...",
    "version": "2025-2",
    "station": "KJFK"
  }
}
```

### Batch Convert (ZIP)

```bash
curl -X POST http://localhost:8001/convert-zip \
  -F "file=@metar_batch.zip" \
  -o results.zip
```

## IWXXM Validation

### Strategy

**Primary**: GIFTs library (mgoberfield/GIFTs)
- XML schema validation
- Structure requirements
- Element validation

**Secondary**: Our validation layer
- Meteorological feature codes (20+)
- Volcanic aviation colors (5)
- Nil reason codes (11)
- Version compatibility

### Supported Features

From `src/schemas/iwxxm_validation.py`:

```python
# Meteorological features
AIRFRAME_ICING, CLOUD, STORM, DUSTSTORM, JETSTREAM, etc. (20+ total)

# Volcanic codes (ICAO Doc 9766)
GREEN, YELLOW, ORANGE, RED, UNASSIGNED

# Nil reasons (WMO standards)
missing, unknown, noSignificantChange, notObservable, etc. (11 total)
```

## Coverage Goals: 90%

### Current Gaps

| Module | Coverage | Gap | Tests Needed |
|--------|----------|-----|--------------|
| api.py | 79% | Error handling | +15 tests |
| conversion.py | 65% | Edge cases | +30 tests |
| security.py | 27% | Full coverage | +20 tests |
| __main__.py | 0% | Entry point | +5 tests |

### Priority for 90% Target

1. **Add API error tests** (400, 403, 500 responses)
2. **Add conversion edge cases** (malformed TAC, boundary conditions)
3. **Add security module tests** (token validation, roles)
4. **Add CLI tests** (__main__.py)

**Estimated**: ~65 additional tests to reach 90%

## Dependencies

### Runtime

```
fastapi>=0.110
uvicorn>=0.23
python-multipart>=0.0.20
pyjwt>=2.8.0
python-jose[cryptography]>=3.3.0
httpx>=0.28.1
```

### Development

```
pytest>=8.4.2
pytest-cov>=4.1.0
skyfield>=1.45
```

### Integration

```
GIFTs (mgoberfield/GIFTs)  - TAC encoding/decoding
```

## Known Limitations

1. **XML→TAC**: Not supported by GIFTs (only TAC→XML)
2. **Security**: 27% coverage - authentication not fully tested
3. **Services**: Placeholder module (0% coverage)
4. **Error Handling**: 21% of api.py error paths untested

## Development Workflow

### Creating New Tests

```python
# tests/test_example.py
import pytest

@pytest.mark.unit
def test_example_feature(sample_fixture):
    """Test description."""
    result = function_under_test(sample_fixture)
    assert result == expected_value
```

### Debugging

```bash
# Verbose with full traceback
pytest tests/ -vv --tb=long

# Drop to pdb on error
pytest tests/ --pdb

# Stop on first failure
pytest tests/ -x
```

### Performance

Current: ~5 seconds for 230 tests
- API tests: <1s
- Schema tests: <1s
- Examples: ~2s
- Roundtrip: ~2s

## References

- **GIFTs**: https://github.com/mgoberfield/GIFTs
- **IWXXM**: https://codes.wmo.int/iwxxm/
- **FastAPI**: https://fastapi.tiangolo.com/
- **pytest**: https://docs.pytest.org/
- **WMO**: https://www.wmo.int/
## Project Structure

```
backend/
├── pyproject.toml         # Project dependencies
├── scripts/               # Utility scripts
├── src/
│   └── backend/
│       ├── __main__.py    # Module entry point for `python -m backend`
│       ├── api.py         # FastAPI application
│       ├── conversion.py  # Conversion logic
│       └── security.py    # Authentication
└── tests/
```
