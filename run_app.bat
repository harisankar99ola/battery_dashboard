@echo off
title Battery Dashboard
echo.
echo ============================================
echo         🔋 Battery Dashboard Launcher
echo ============================================
echo.

REM Check if we're in the right directory
if not exist "src\main.py" (
    echo ❌ Error: src\main.py not found
    echo Please run this script from the battery-dashboard directory
    echo.
    pause
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Check for credentials
if not exist "credentials.json" (
    echo ⚠️  Warning: credentials.json not found
    echo Run setup_credentials.bat first to set up Google Drive API
    echo.
    pause
    exit /b 1
)

echo ✓ Credentials found
echo.

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo ✓ Virtual environment found, activating...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found, using system Python
)

echo.
echo 🚀 Starting Battery Dashboard...
echo.
echo Backend will start on: http://localhost:8000
echo Frontend will start on: http://localhost:8050
echo.
echo Dashboard will open automatically in your browser
echo.
echo Press Ctrl+C to stop the application
echo.

REM Run the main application
python src\main.py

if errorlevel 1 (
    echo.
    echo ❌ Application stopped with error
    echo Check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Application stopped normally
pause
