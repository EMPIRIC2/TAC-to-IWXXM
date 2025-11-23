@echo off
REM Launch script for METAR to IWXXM Converter GUI (Windows Command Prompt)
REM Usage: launch_gui.bat [port] [host]

setlocal enabledelayedexpansion

REM Get script directory and repository root
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "VENV_DIR=%REPO_ROOT%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

REM Default values
set "HOST=0.0.0.0"
set "PORT=8000"
set "RELOAD_ARG=--no-reload"

REM Parse arguments
if not "%1"=="" set "PORT=%1"
if not "%2"=="" set "HOST=%2"
if "%1"=="--help" goto :show_help
if "%1"=="/?" goto :show_help
if "%1"=="--reload" set "RELOAD_ARG=--reload"
if "%2"=="--reload" set "RELOAD_ARG=--reload"

cd /d "%REPO_ROOT%"

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo [ERROR] Virtual environment not found at %VENV_DIR%
    echo.
    echo Please create it first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install fastapi uvicorn tpg python-multipart
    exit /b 1
)

REM Check if Python executable exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python executable not found at %PYTHON_EXE%
    exit /b 1
)

echo [INFO] Using virtual environment: %VENV_DIR%

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
"%PYTHON_EXE%" -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [WARN] Required dependencies not found
    echo [INFO] Installing dependencies...
    "%PYTHON_EXE%" -m pip install fastapi uvicorn tpg python-multipart
)

REM Launch the application
echo.
echo ========================================
echo  METAR to IWXXM Converter GUI
echo ========================================
echo  Server:   http://%HOST%:%PORT%
echo  API Docs: http://localhost:%PORT%/docs
echo  ReDoc:    http://localhost:%PORT%/redoc
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.

"%PYTHON_EXE%" -m uvicorn gui.app:app --host %HOST% --port %PORT% %RELOAD_ARG%
goto :eof

:show_help
echo Usage: launch_gui.bat [PORT] [HOST] [--reload]
echo.
echo Arguments:
echo   PORT      Port to listen on (default: 8000)
echo   HOST      Host to bind to (default: 0.0.0.0)
echo   --reload  Enable auto-reload on code changes
echo.
echo Examples:
echo   launch_gui.bat
echo   launch_gui.bat 5000
echo   launch_gui.bat 5000 127.0.0.1
echo   launch_gui.bat 8000 0.0.0.0 --reload
goto :eof
