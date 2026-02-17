@echo off
REM Launch script for METAR to IWXXM Backend API (Windows Batch)
REM Usage: launch_api.bat [PORT] [HOST] [--reload]

setlocal

REM Default values
set "HOST=0.0.0.0"
set "PORT=8001"
set "RELOAD="

REM Parse arguments
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="/?" goto :help

if not "%1"=="" set PORT=%1
if not "%2"=="" set HOST=%2
if "%3"=="--reload" set RELOAD=--reload

REM Get script directory and repository root
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "VENV_DIR=%REPO_ROOT%\.venv"

cd /d "%REPO_ROOT%"

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo ❌ Virtual environment not found at %VENV_DIR%
    echo.
    echo Please create it first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate.bat
    echo   pip install fastapi uvicorn tpg python-multipart
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Check if dependencies are installed
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo ❌ Required dependencies not found
    echo.
    echo Installing dependencies...
    python -m pip install fastapi uvicorn tpg python-multipart
)

REM Launch the backend API
echo 🚀 Starting METAR to IWXXM Backend API...
echo 📡 Server: http://%HOST%:%PORT%
echo 📚 API Docs: http://localhost:%PORT%/docs
echo 📖 ReDoc: http://localhost:%PORT%/redoc
echo 💚 Health: http://localhost:%PORT%/health
echo.
echo Press CTRL+C to stop the server
echo.

python -m uvicorn backend.api:app --host %HOST% --port %PORT% %RELOAD%
goto :eof

:help
echo Usage: launch_api.bat [PORT] [HOST] [--reload]
echo.
echo Launch the METAR to IWXXM Backend API server
echo.
echo Arguments:
echo   PORT        Port to listen on (default: 8001)
echo   HOST        Host to bind to (default: 0.0.0.0)
echo   --reload    Enable auto-reload on code changes
echo.
echo Examples:
echo   launch_api.bat
echo   launch_api.bat 8001
echo   launch_api.bat 8001 0.0.0.0 --reload
exit /b 0
