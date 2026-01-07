@echo off
REM Launch script for METAR to IWXXM Converter Frontend (Windows Command Prompt)
REM Usage: launch_gui.bat

setlocal enabledelayedexpansion

REM Get script directory and repository root
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "FRONTEND_DIR=%REPO_ROOT%\frontend"

REM Check if frontend directory exists
if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found at: %FRONTEND_DIR%
    echo [INFO] Please ensure the frontend submodule is initialized:
    echo [INFO]   git submodule update --init --recursive
    exit /b 1
)
if "%1"=="--help" goto :show_help

REM Change to frontend directory
cd /d "%FRONTEND_DIR%"

REM Check if node_modules exists
if not exist "%FRONTEND_DIR%\\node_modules" (
    echo [INFO] Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        exit /b 1
    )
)

REM Launch the frontend dev server
echo.
echo ========================================
echo  METAR to IWXXM Converter Frontend
echo ========================================
echo  Server will start at http://localhost:5173
echo  (Vite default port)
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.

call npm run dev
goto :eof

:show_help
echo Usage: launch_gui.bat
echo.
echo This script launches the React/Vite frontend development server.
echo No arguments required - Vite uses default port 5173.
echo.
echo Example:
echo   launch_gui.bat
goto :eof

