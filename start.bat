@echo off
title Battery Dashboard - Starting Services
echo.
echo ================================================
echo 🚀 STARTING BATTERY DASHBOARD SERVICES
echo ================================================
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check for virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  No virtual environment found - using system Python
)

echo.

REM Check for required files
if not exist "src\main.py" (
    echo ❌ src\main.py not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

if not exist "src\backend\main_simple.py" (
    echo ❌ src\backend\main_simple.py not found
    echo Backend server file missing
    pause
    exit /b 1
)

if not exist "src\frontend\app.py" (
    echo ❌ src\frontend\app.py not found
    echo Frontend dashboard file missing
    pause
    exit /b 1
)

echo ✅ Required files found
echo.

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo 📦 Installing/updating dependencies...
    python -m pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo ⚠️  Some dependencies may have issues, but continuing...
    ) else (
        echo ✅ Dependencies installed
    )
    echo.
)

REM Check for credentials
echo 🔐 Checking for Google Drive credentials...
if exist "credentials.json" (
    echo ✅ credentials.json found
) else if exist "client_secret*.json" (
    echo ✅ Client secret file found
) else (
    echo ⚠️  No Google Drive credentials found
    echo You may need to set up credentials using setup_credentials.bat
    echo.
)

REM Stop any existing services
echo 🛑 Stopping any existing services...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo 🚀 Starting Battery Dashboard...
echo.
echo Backend will start on: http://localhost:8000
echo Frontend will start on: http://localhost:8050
echo.
echo Press Ctrl+C to stop the services
echo.

REM Start the main application
python src\main.py

echo.
echo 🛑 Services stopped
pause
