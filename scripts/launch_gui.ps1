# Launch script for METAR to IWXXM Converter GUI (PowerShell)
# Usage: .\launch_gui.ps1 [-Port 8000] [-Host "0.0.0.0"] [-Reload]

param(
    [int]$Port = 8000,
    [string]$HostAddress = "0.0.0.0",
    [switch]$Reload,
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\launch_gui.ps1 [OPTIONS]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Port <int>            Port to listen on (default: 8000)"
    Write-Host "  -HostAddress <string>  Host to bind to (default: 0.0.0.0)"
    Write-Host "  -Reload                Enable auto-reload on code changes"
    Write-Host "  -Help                  Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\launch_gui.ps1"
    Write-Host "  .\launch_gui.ps1 -Port 5000"
    Write-Host "  .\launch_gui.ps1 -HostAddress 127.0.0.1 -Reload"
    exit 0
}

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $RepoRoot ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

Set-Location $RepoRoot

# Check if virtual environment exists
if (-not (Test-Path $VenvDir)) {
    Write-Host "❌ Virtual environment not found at $VenvDir" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create it first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv"
    Write-Host "  .venv\Scripts\Activate.ps1"
    Write-Host "  pip install fastapi uvicorn tpg python-multipart"
    exit 1
}

# Check if Python executable exists
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Python executable not found at $PythonExe" -ForegroundColor Red
    exit 1
}

Write-Host "Using virtual environment: $VenvDir" -ForegroundColor Green

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
try {
    & $PythonExe -c "import fastapi, uvicorn" 2>$null
} catch {
    Write-Host "❌ Required dependencies not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & $PythonExe -m pip install fastapi uvicorn tpg python-multipart
}

# Build command arguments
$ReloadArg = if ($Reload) { "--reload" } else { "--no-reload" }

# Launch the application
Write-Host ""
Write-Host "Starting METAR to IWXXM Converter GUI..." -ForegroundColor Green
Write-Host "Server: http://$($HostAddress):$Port" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:$Port/docs" -ForegroundColor Cyan
Write-Host "ReDoc: http://localhost:$Port/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Launch uvicorn
& $PythonExe -m uvicorn gui.app:app --host $HostAddress --port $Port $ReloadArg
