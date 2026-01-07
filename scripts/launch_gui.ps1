# Launch script for METAR to IWXXM Converter Frontend (PowerShell)
# Usage: .\launch_gui.ps1 [-Help]

param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\launch_gui.ps1 [OPTIONS]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Options:"
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
$FrontendDir = Join-Path $RepoRoot "frontend"

# Check if frontend directory exists
if (-not (Test-Path $FrontendDir)) {
    Write-Host "❌ Frontend directory not found at $FrontendDir" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure the frontend submodule is initialized:" -ForegroundColor Yellow
    Write-Host "  git submodule update --init --recursive"
    exit 1
}

Set-Location $FrontendDir

# Check if node_modules exists
if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Launch the frontend dev server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " METAR to IWXXM Converter Frontend" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Server will start at http://localhost:5173" -ForegroundColor Yellow
Write-Host " (Vite default port)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm run dev

