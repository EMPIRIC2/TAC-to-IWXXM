# Launch Scripts for METAR to IWXXM Converter

This directory contains platform-specific launch scripts for the METAR to IWXXM Converter React frontend application.

## Available Scripts

### PowerShell (Windows)
**File**: `launch_gui.ps1`

```powershell
# Show help
.\launch_gui.ps1 -Help

# Launch frontend dev server
.\launch_gui.ps1
```

**Parameters**:
- `-Help` - Show help message

---

### Bash (Linux/macOS)
**File**: `launch_gui.sh`

```bash
# Make executable (first time only)
chmod +x launch_gui.sh

# Launch frontend dev server
./launch_gui.sh
```

**Options**:
- `--help` - Show help message

---

### Command Prompt (Windows)
**File**: `launch_gui.bat`

```cmd
REM Launch frontend dev server
launch_gui.bat
```

---

## Prerequisites

All scripts require:

1. **Node.js and npm** - Frontend is built with React/Vite
   ```bash
   # Check if installed
   node --version
   npm --version
   ```

2. **Frontend Submodule** - Must be initialized:
   ```bash
   git submodule update --init --recursive
   ```

3. **Dependencies** - Scripts will auto-install if missing, or install manually:
   ```bash
   cd frontend
   npm install
   ```

---

## What These Scripts Do

1. ✅ Check if frontend submodule exists
2. ✅ Install npm dependencies if node_modules is missing
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

### Frontend submodule not found

```bash
git submodule update --init --recursive
```

### Dependencies not installing

```bash
cd frontend
npm install
```

### Port already in use

Vite uses port 5173 by default. If this port is in use, Vite will automatically try the next available port (5174, 5175, etc.).
