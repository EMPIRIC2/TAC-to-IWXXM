# Launch Scripts

Platform-specific scripts for starting the METAR to IWXXM Converter services.

macOS and Linux use the repo-root `start-dev-servers.sh` launcher (API port 18001). This folder keeps the Windows scripts.

## Frontend (GUI) Scripts

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
- Check for required dependencies
- Provide helpful error messages
- Support development mode with hot reloading
- Include troubleshooting information

## Troubleshooting

### PowerShell Execution Policy Error
If you see "cannot be loaded because running scripts is disabled":
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Port Already in Use
- Local macOS/Linux stack: `start-dev-servers.sh` uses API port 18001 and the frontend port from that script.

## Production Deployment

For production, use Docker Compose instead:
```bash
docker compose up --build
```

This provides optimized builds with nginx and proper service orchestration.
