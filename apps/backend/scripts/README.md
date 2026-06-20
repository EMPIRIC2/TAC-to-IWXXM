# Backend Scripts

Utility and maintenance scripts for the METAR to IWXXM backend.

## Quick Start

Run scripts from the backend directory:

```bash
cd backend

# Development server
./scripts/start_dev.sh

# Data operations
python scripts/generate_test_data.py
python scripts/update_airports_db.py

# Validation
python scripts/validate_generated_xml_schematron.py <xml_file>

# Analysis
python scripts/analyze_version_comparisons.py
```

## Available Scripts

### Development

#### start_dev.sh

Start the development server with auto-reload.

**Usage:**

```bash
./scripts/start_dev.sh
```

**What it does:**

- Starts FastAPI development server on port 8000
- Enables auto-reload on code changes
- Loads environment from `.env`

### Data & Airport Management

#### update_airports_db.py

Update the airport database with current data.

**Usage:**

```bash
python scripts/update_airports_db.py
```

**What it does:**

- Fetches current airport data from configured sources
- Updates airport metadata (elevation, coordinates, etc.)
- Refreshes airport validation data

#### fetch_openaip_airports.py

Fetch airport data from OpenAIP service.

**Usage:**

```bash
python scripts/fetch_openaip_airports.py [--output airports.json]
```

**What it does:**

- Downloads OpenAIP airport database
- Converts to internal format
- Caches for local development

#### mirror_wmo_bundles.py

Mirror WMO schema bundles locally for testing.

**Usage:**

```bash
python scripts/mirror_wmo_bundles.py [--version 2025-2]
```

**What it does:**

- Downloads IWXXM schema bundles from WMO
- Stores locally in `schemas/` directory
- Enables offline schema validation

### Validation

#### validate_generated_xml_schematron.py

Validate generated XML files against Schematron rules.

**Usage:**

```bash
python scripts/validate_generated_xml_schematron.py <xml_file> [--verbose]
python scripts/validate_generated_xml_schematron.py output.xml
python scripts/validate_generated_xml_schematron.py *.xml  # Validate multiple files
```

**Options:**

- `--verbose` - Detailed validation output
- `--rules <file>` - Custom Schematron rules
- `--version <version>` - IWXXM version (default: 2025-2)

**What it does:**

- Validates XML against IWXXM Schematron rules
- Reports detailed errors and warnings
- Supports batch validation

### Testing & Data Generation

#### generate_test_data.py

Generate synthetic METAR test data.

**Usage:**

```bash
python scripts/generate_test_data.py \
  --count 100 \
  --stations KJFK,NLNG \
  --output test_metars.txt
```

**Options:**

- `--count <n>` - Number of METAR to generate
- `--stations <list>` - Comma-separated station codes
- `--output <file>` - Output file

**What it does:**

- Generates realistic METAR strings
- Includes various weather phenomena
- Creates test dataset for validation

#### test_sprint1_data_integration.py

Integration test for sprint 1 data requirements.

**Usage:**

```bash
python scripts/test_sprint1_data_integration.py [--verbose]
```

**What it does:**

- Tests complete METAR to IWXXM workflow
- Validates data integration points
- Reports sprint 1 compliance

### Analysis & Comparison

#### analyze_version_comparisons.py

Analyze differences between IWXXM versions.

**Usage:**

```bash
python scripts/analyze_version_comparisons.py [--versions 2023-1,2025-2]
```

**What it does:**

- Compares IWXXM schema versions
- Identifies breaking changes
- Analyzes element differences

#### compare_iwxxm_versions.sh

Shell script for comparing IWXXM version outputs.

**Usage:**

```bash
./scripts/compare_iwxxm_versions.sh <version1> <version2>
./scripts/compare_iwxxm_versions.sh 2023-1 2025-2
```

**What it does:**

- Compares conversion output across versions
- Validates backward compatibility
- Generates comparison report

## Common Workflows

### Setup Development Environment

```bash
# 1. Clone and setup
git clone <repo>
cd backend

# 2. Start development server
./scripts/start_dev.sh

# 3. In another terminal, run tests
pytest tests/smoke.py -v
```

### Update Data

```bash
# 1. Fetch airport data
python scripts/fetch_openaip_airports.py

# 2. Update database
python scripts/update_airports_db.py

# 3. Mirror schemas
python scripts/mirror_wmo_bundles.py --version 2025-2
```

### Validate New Conversion

```bash
# 1. Generate test METAR
python scripts/generate_test_data.py --count 10

# 2. Convert via API
# (Use curl or Python client)

# 3. Validate output
python scripts/validate_generated_xml_schematron.py output.xml --verbose
```

### Compare Versions

```bash
# 1. Generate output for version 1
# (Set IWXXM_VERSION=2023-1)
python scripts/generate_test_data.py

# 2. Generate output for version 2
# (Set IWXXM_VERSION=2025-2)
python scripts/generate_test_data.py

# 3. Compare
./scripts/compare_iwxxm_versions.sh 2023-1 2025-2
```

## Dependencies

Scripts use dependencies from `pyproject.toml`:

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Or use uv run
uv run python scripts/script_name.py
```

## Environment Variables

Configure scripts via `.env`:

```
# Data sources
OPENAIP_URL=https://api.openaip.net/api/airports
WMO_BUNDLE_URL=https://wmo-im/iwxxm/bundles/

# Processing
IWXXM_VERSION=2025-2
VALIDATION_STRICT=true
LOG_LEVEL=info
```

## Error Handling

Scripts generally exit with:

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Data/network error

Check error output:

```bash
python scripts/script_name.py 2>&1 | head -20
```

## Adding New Scripts

1. Create script in this directory with `script_name.py`
2. Add docstring explaining purpose
3. Use argparse for CLI arguments
4. Add to this README in appropriate section
5. Test with: `python scripts/script_name.py --help`

## Troubleshooting

### Import errors

```bash
# Ensure backend dir in PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python scripts/script_name.py
```

### Network errors (mirror/fetch)

```bash
# Check connectivity
curl https://api.openaip.net

# Use proxy if needed
export HTTP_PROXY=...
```

### Database errors

```bash
# Check DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
python -c "import psycopg; psycopg.connect('$DATABASE_URL')"
```

---

See [BACKEND_STRUCTURE.md](../BACKEND_STRUCTURE.md) for overall organization.
For more help, check inline script documentation: `python scripts/script_name.py --help`
