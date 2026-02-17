# Launch script for METAR to IWXXM Backend API (PowerShell)
# Usage: .\launch_api.ps1 [-Port 8001] [-Host "0.0.0.0"] [-Reload]

param(
    [string]$Host = "0.0.0.0",
    [int]$Port = 8001,
    [switch]$Reload,
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\launch_api.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Launch the METAR to IWXXM Backend API server"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Port <PORT>     Port to listen on (default: 8001)"
    Write-Host "  -Host <HOST>     Host to bind to (default: 0.0.0.0)"
    Write-Host "  -Reload          Enable auto-reload on code changes"
    Write-Host "  -Help            Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\launch_api.ps1"
    Write-Host "  .\launch_api.ps1 -Port 8001 -Reload"
    exit 0
}

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $RepoRoot ".venv"

Set-Location $RepoRoot

# Check if virtual environment exists
if (-not (Test-Path $VenvDir)) {
    Write-Host "❌ Virtual environment not found at $VenvDir" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create it first:"
    Write-Host "  python -m venv .venv"
    Write-Host "  .venv\Scripts\Activate.ps1"
    Write-Host "  pip install fastapi uvicorn tpg python-multipart"
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
& $ActivateScript

# Check if dependencies are installed
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$CheckDeps = & $PythonExe -c "import fastapi, uvicorn" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Required dependencies not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing dependencies..."
    & $PythonExe -m pip install fastapi uvicorn tpg python-multipart
}

# Build uvicorn command
$ReloadArg = if ($Reload) { "--reload" } else { "" }

# Launch the backend API
Write-Host "🚀 Starting METAR to IWXXM Backend API..." -ForegroundColor Green
Write-Host "📡 Server: http://${Host}:${Port}"
Write-Host "📚 API Docs: http://localhost:${Port}/docs"
Write-Host "📖 ReDoc: http://localhost:${Port}/redoc"
Write-Host "💚 Health: http://localhost:${Port}/health"
Write-Host ""
Write-Host "Press CTRL+C to stop the server"
Write-Host ""

if ($ReloadArg) {
    & $PythonExe -m uvicorn backend.api:app --host $Host --port $Port --reload
} else {
    & $PythonExe -m uvicorn backend.api:app --host $Host --port $Port
}
