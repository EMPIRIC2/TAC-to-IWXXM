# Launch Scripts for METAR to IWXXM Converter

This directory contains platform-specific launch scripts for the METAR to IWXXM Converter GUI application.

## Available Scripts

### PowerShell (Windows)
**File**: `launch_gui.ps1`

```powershell
# Show help
.\launch_gui.ps1 -Help

# Launch with defaults (0.0.0.0:8000)
.\launch_gui.ps1

# Custom port
.\launch_gui.ps1 -Port 5000

# Custom host and port
.\launch_gui.ps1 -HostAddress 127.0.0.1 -Port 5000

# Enable auto-reload for development
.\launch_gui.ps1 -Reload
```

**Parameters**:
- `-Port <int>` - Port to listen on (default: 8000)
- `-HostAddress <string>` - Host to bind to (default: 0.0.0.0)
- `-Reload` - Enable auto-reload on code changes
- `-Help` - Show help message

---

### Bash (Linux/macOS)
**File**: `launch_gui.sh`

```bash
# Make executable (first time only)
chmod +x launch_gui.sh

# Show help
./launch_gui.sh --help

# Launch with defaults (0.0.0.0:8000)
./launch_gui.sh

# Custom port
./launch_gui.sh --port 5000

# Custom host and port
./launch_gui.sh --host 127.0.0.1 --port 5000

# Enable auto-reload for development
./launch_gui.sh --reload
```

**Options**:
- `--port PORT` - Port to listen on (default: 8000)
- `--host HOST` - Host to bind to (default: 0.0.0.0)
- `--reload` - Enable auto-reload on code changes
- `--help` - Show help message

---

### Command Prompt (Windows)
**File**: `launch_gui.bat`

```cmd
REM Show help
launch_gui.bat --help

REM Launch with defaults (0.0.0.0:8000)
launch_gui.bat

REM Custom port
launch_gui.bat 5000

REM Custom host and port
launch_gui.bat 5000 127.0.0.1

REM Enable auto-reload
launch_gui.bat 8000 0.0.0.0 --reload
```

**Arguments**:
1. `PORT` - Port to listen on (default: 8000)
2. `HOST` - Host to bind to (default: 0.0.0.0)
3. `--reload` - Enable auto-reload on code changes

---

## Prerequisites

All scripts require:

1. **Virtual Environment** - Scripts expect `.venv` directory in repository root
   ```bash
   python -m venv .venv
   ```

2. **Dependencies** - Scripts will auto-install if missing, or install manually:
   ```bash
   # Activate virtual environment first
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   
   # Install dependencies
   pip install fastapi uvicorn tpg python-multipart
   ```

---

## What These Scripts Do

1. ✅ Locate and activate the virtual environment
2. ✅ Check for required dependencies (auto-install if missing)
3. ✅ Launch the FastAPI application via uvicorn
4. ✅ Display server URLs for easy access:
   - Main app: `http://localhost:8000/`
   - API docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

## Development vs Production

### Development Mode (with auto-reload)
```powershell
# PowerShell
.\launch_gui.ps1 -Reload

# Bash
./launch_gui.sh --reload

# Batch
launch_gui.bat 8000 0.0.0.0 --reload
```

Auto-reload watches for code changes and automatically restarts the server. Use this during development.

### Production Mode (default)
```powershell
# PowerShell
.\launch_gui.ps1

# Bash
./launch_gui.sh

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

## Network Access

- **`0.0.0.0`** (default) - Accessible from any network interface (allows external connections)
- **`127.0.0.1`** - Localhost only (restricts to local machine)

For security, use `127.0.0.1` if you don't need external access.
