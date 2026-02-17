# Launch Scripts

Platform-specific scripts for starting the METAR to IWXXM Converter services.

## Frontend (GUI) Scripts

### launch_gui.sh (Linux/macOS)
Bash script for launching the frontend development server.

```bash
# Make executable (first time only)
chmod +x launch_gui.sh

# Launch
./launch_gui.sh
```

**Features:**
- Checks for Node.js and npm installation
- Verifies frontend submodule exists
- Auto-installs dependencies if needed
- Starts Vite dev server on http://localhost:5173

### launch_gui.ps1 (Windows PowerShell)
PowerShell script with the same functionality as the bash version.

```powershell
# Show help
.\launch_gui.ps1 -Help

# Launch
.\launch_gui.ps1
```

### launch_gui.bat (Windows Command Prompt)
Batch file for Windows Command Prompt.

```cmd
launch_gui.bat
```

## Backend (API) Scripts

### launch_api.sh (Linux/macOS)
Bash script for launching the FastAPI backend server.

```bash
# Make executable (first time only)
chmod +x launch_api.sh

# Launch
./launch_api.sh
```

**Features:**
- Checks for Python 3.7+
- Verifies virtual environment exists
- Auto-installs dependencies if needed
- Starts uvicorn server on http://localhost:8001

### launch_api.ps1 (Windows PowerShell)
PowerShell script with the same functionality.

```powershell
# Launch
.\launch_api.ps1
```

### launch_api.bat (Windows Command Prompt)
Batch file for Windows Command Prompt.

```cmd
launch_api.bat
```

## Common Features

All scripts:
- ✅ Check for required dependencies
- ✅ Provide helpful error messages
- ✅ Support development mode with hot reloading
- ✅ Include troubleshooting information

## Troubleshooting

### PowerShell Execution Policy Error
If you see "cannot be loaded because running scripts is disabled":
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Bash Permission Denied
```bash
chmod +x launch_*.sh
```

### Port Already in Use
- Frontend (Vite): Default port 5173, auto-increments if busy (5174, 5175, etc.)
- Backend (uvicorn): Default port 8001, can be changed in the script

## Production Deployment

For production, use Docker Compose instead:
```bash
docker-compose up --build
```

This provides optimized builds with nginx and proper service orchestration.
