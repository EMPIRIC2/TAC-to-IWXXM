# Scripts Directory

This directory contains organized utility scripts, database setup scripts, and launch scripts for the METAR to IWXXM Converter project.

## Coverage gate (EV-080 / #1077)

Per [ADR-007](../docs/adr/ADR-007-universal-coverage-gate.md): every `scripts/**/*.py` is
measured under a dedicated **100%** line+branch coverage job; every `scripts/**/*.sh` has
≥1 **bats-core** test in CI (`tests/bats/`). Local entrypoints (EV-080 tech-tooling):

```bash
make test-coverage-scripts   # pytest tests/scripts --cov=scripts (scaffold until M4)
make test-bats               # bats tests/bats (scaffold until M4)
```

Approved omits do not apply to these scripts themselves.

## Directory Structure

### 📁 [launchers/](launchers/)
Platform-specific launch scripts for starting the frontend (GUI) and backend (API) services.
- Shell scripts for Linux/macOS (`.sh`)
- PowerShell scripts for Windows (`.ps1`)
- Batch scripts for Windows Command Prompt (`.bat`)

### 📁 [db-setup/](db-setup/)
Database table creation and setup scripts for Supabase.
- `create_evaluation_tables.sql` - Evaluation jobs and results tables
- `create_translation_statistics_tables.sql` - Translation statistics tables

### 📁 [utilities/](utilities/)
Active utility scripts for data processing and administration.
- `parse_airports_csv.py` - Parse airport data from CSV files
- `extract_email_templates.py` - Extract email templates from Supabase
- `upload_email_templates.py` - Upload email templates to Supabase
- `create_admin_user.py` - Create admin users in the database
- `syntax_check.py` - Validate Python file syntax before committing changes

### 📦 Archived Scripts
Historical debug, fix, and diagnostic scripts have been moved to `/docs/ARCHIVE/scripts/db-debug-fixes/` to keep this directory focused on active tools.

---

## Launch Scripts

Platform-specific scripts for starting services are located in [launchers/](launchers/).

### GUI (Frontend)

#### PowerShell (Windows)
**File**: `launchers/launch_gui.ps1`

```powershell
# Show help
.\launchers\launch_gui.ps1 -Help

# Launch frontend dev server
.\launchers\launch_gui.ps1
```

#### Bash (Linux/macOS)
**File**: `launchers/launch_gui.sh`

```bash
# Make executable (first time only)
chmod +x launchers/launch_gui.sh

# Launch frontend dev server
./launchers/launch_gui.sh
```

#### Command Prompt (Windows)
**File**: `launchers/launch_gui.bat`

```cmd
REM Launch frontend dev server
launchers\launch_gui.bat
```

### API (Backend)

Similar launch scripts are available for the backend API:
- `launchers/launch_api.ps1` (PowerShell)
- `launchers/launch_api.sh` (Bash)
- `launchers/launch_api.bat` (Command Prompt)

---

## Database Setup Scripts

SQL scripts for creating database tables are in [db-setup/](db-setup/).

### Running Database Setup Scripts

Execute these scripts in the Supabase Dashboard SQL Editor or using `psql`:

```bash
# Using psql
psql -h your-db-host -U postgres -d postgres -f db-setup/create_evaluation_tables.sql

# Or in Supabase Dashboard
# Navigate to SQL Editor and paste the script contents
```

### Available Scripts

- **`create_evaluation_tables.sql`** - Creates evaluation job tracking tables:
  - `evaluation_jobs` - Job status and metadata
  - `evaluation_results` - Individual evaluation results
  - `evaluation_stats` - Aggregated statistics

- **`create_translation_statistics_tables.sql`** - Creates translation statistics tables for tracking conversion metrics

---

## Utility Scripts

Active utility scripts are in [utilities/](utilities/).

### Airport Data Parsing
```bash
python utilities/parse_airports_csv.py
```

### Email Template Management
```bash
# Extract templates from Supabase
python utilities/extract_email_templates.py

# Upload templates to Supabase
python utilities/upload_email_templates.py
```

### Admin User Creation
```bash
python utilities/create_admin_user.py
```

### Syntax Validation

Validate Python file syntax to catch errors before committing:

```bash
# Check single file
python3 utilities/syntax_check.py backend/tests/test_module.py

# Check entire directory
python3 utilities/syntax_check.py backend/tests/

# Check all Python files in project
python3 utilities/syntax_check.py --all
```

**Output examples:**
```
Checking 72 Python file(s)...
✓ backend/tests/test_api.py
✓ backend/tests/test_evaluation.py
✗ backend/tests/test_broken.py

======================================================================
Checked: 72 files
Passed:  71 files
Failed:  1 files

======================================================================
SYNTAX ERRORS:
======================================================================

backend/tests/test_broken.py:
  File "backend/tests/test_broken.py", line 45
    def test airport_region(self, client):
             ^^^^^^^^^^^^^^^^^^^
  SyntaxError: expected '('
```

**Common errors detected:**
- Missing underscores in function names
- Unclosed parentheses/brackets/quotes
- Missing colons after function/class definitions
- Invalid indentation

---

## Prerequisites

All scripts require:

1. **Node.js and npm** - Frontend is built with React/Vite
   ```bash
   # Check if installed
   node --version
   npm --version
   ```

2. **Frontend app** — lives at `apps/frontend` in the monorepo:

   ```bash
   cd apps/frontend
   pnpm install
   ```

---

## What These Scripts Do

1. ✅ Check if `apps/frontend` exists
2. ✅ Install npm/pnpm dependencies if node_modules is missing
3. ✅ Launch the Vite development server
4. ✅ Server starts at `http://localhost:5173` (Vite default)

The Vite dev server includes:
- Hot Module Replacement (HMR) for instant updates
- Fast builds with native ES modules
- Automatic browser refresh on file changes

---

## Development Mode

```powershell
# PowerShell
.\launch_gui.ps1

# Bash
./launch_gui.sh

# Batch
launch_gui.bat
```

The Vite development server automatically includes hot reloading and watches for file changes.

# Batch
launch_gui.bat
```

No auto-reload for better performance in production.

---

## Troubleshooting

### PowerShell Execution Policy Error
If you see "cannot be loaded because running scripts is disabled":
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Bash Permission Denied
If you see "Permission denied":
```bash
chmod +x launch_gui.sh
```

### Virtual Environment Not Found
Create the virtual environment:
```bash
python -m venv .venv
```

### Dependencies Not Found
Install manually:
```bash
# Activate venv first, then:
pip install fastapi uvicorn tpg python-multipart
```

---

## Accessing the Application

Once launched, open your browser to:

- **Main Application**: http://localhost:8000/
- **Interactive API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Stopping the Server

Press `CTRL+C` in the terminal where the script is running.

---

## Production Deployment

For production deployment, use Docker Compose which serves the built frontend via nginx:

```bash
docker-compose up --build
```

This will:
- Build the frontend with optimized production settings
- Serve static assets via nginx on port 80 (mapped to host port 8000)
- Configure nginx to proxy API and auth requests to backend services

---

## Troubleshooting

### Frontend app not found

```bash
make install
```

### Dependencies not installing

```bash
cd frontend
npm install
```

### Port already in use

Vite uses port 5173 by default. If this port is in use, Vite will automatically try the next available port (5174, 5175, etc.).
