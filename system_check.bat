@echo off
title Battery Dashboard - System Check
echo.
echo ============================================
echo    Battery Dashboard - System Verification
echo ============================================
echo.

echo 🔍 Checking system requirements and installation...
echo.

REM Check project structure
echo 📁 Project Structure:
if exist "src\main.py" (
    echo ✓ src\main.py - Main application entry point
) else (
    echo ❌ src\main.py - MISSING
)

if exist "src\backend\main.py" (
    echo ✓ src\backend\main.py - Backend server
) else (
    echo ❌ src\backend\main.py - MISSING
)

if exist "src\frontend\app.py" (
    echo ✓ src\frontend\app.py - Frontend dashboard
) else (
    echo ❌ src\frontend\app.py - MISSING
)

if exist "requirements.txt" (
    echo ✓ requirements.txt - Dependencies list
) else (
    echo ❌ requirements.txt - MISSING
)

echo.

REM Check Python and dependencies
echo 🐍 Python Environment:
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python - NOT FOUND
) else (
    echo ✓ Python - FOUND
)

if exist "venv\Scripts\python.exe" (
    echo ✓ Virtual Environment - FOUND
) else (
    echo ⚠️  Virtual Environment - NOT FOUND (optional)
)

echo.

REM Check key dependencies (only if Python is available)
python --version >nul 2>&1
if not errorlevel 1 (
    echo 📦 Key Dependencies:
    
    python -c "import fastapi; print('✓ FastAPI - Version:', fastapi.__version__)" 2>nul
    if errorlevel 1 echo ❌ FastAPI - NOT INSTALLED
    
    python -c "import dash; print('✓ Dash - Version:', dash.__version__)" 2>nul
    if errorlevel 1 echo ❌ Dash - NOT INSTALLED
    
    python -c "import pandas; print('✓ Pandas - Version:', pandas.__version__)" 2>nul
    if errorlevel 1 echo ❌ Pandas - NOT INSTALLED
    
    python -c "import plotly; print('✓ Plotly - Version:', plotly.__version__)" 2>nul
    if errorlevel 1 echo ❌ Plotly - NOT INSTALLED
    
    echo.
)

REM Check credentials
echo 🔑 Credentials:
if exist "credentials.json" (
    echo ✓ credentials.json - Google Drive API credentials found
) else (
    echo ❌ credentials.json - MISSING (required for Google Drive access)
)

if exist "token.json" (
    echo ✓ token.json - Authentication token found
) else (
    echo ⚠️  token.json - NOT FOUND (will be created on first run)
)

echo.

REM Check utilities
echo 🛠️  Utility Scripts:
if exist "installer.bat" (
    echo ✓ installer.bat - Installation script
) else (
    echo ❌ installer.bat - MISSING
)

if exist "setup_credentials.bat" (
    echo ✓ setup_credentials.bat - Credential setup helper
) else (
    echo ❌ setup_credentials.bat - MISSING
)

if exist "start.bat" (
    echo ✓ start.bat - Application starter
) else (
    echo ❌ start.bat - MISSING
)

if exist "stop.bat" (
    echo ✓ stop.bat - Application stopper
) else (
    echo ❌ stop.bat - MISSING
)

echo.

REM Port availability check
echo 🌐 Port Availability:
netstat -an | find "LISTENING" | find ":8000" >nul
if errorlevel 1 (
    echo ✓ Port 8000 - Available for backend
) else (
    echo ⚠️  Port 8000 - In use (may cause conflicts)
)

netstat -an | find "LISTENING" | find ":8050" >nul
if errorlevel 1 (
    echo ✓ Port 8050 - Available for frontend
) else (
    echo ⚠️  Port 8050 - In use (may cause conflicts)
)

echo.

REM Overall status
echo ============================================
echo               SYSTEM STATUS
echo ============================================

set "all_good=1"

if not exist "src\main.py" set "all_good=0"
if not exist "requirements.txt" set "all_good=0"
if not exist "credentials.json" set "all_good=0"

python --version >nul 2>&1
if errorlevel 1 set "all_good=0"

if "%all_good%"=="1" (
    echo.
    echo ✅ SYSTEM READY!
    echo Battery Dashboard is properly configured and ready to run.
    echo.
    echo Next steps:
    echo 1. Run: start.bat
    echo 2. Access dashboard at: http://localhost:8050
    echo.
) else (
    echo.
    echo ❌ SYSTEM NOT READY
    echo Please address the missing components above.
    echo.
    if not exist "credentials.json" (
        echo • Run setup_credentials.bat for Google Drive setup
    )
    echo • Check README.md for detailed instructions
    echo.
)

echo ============================================
echo.

set /p "run_now=Do you want to try running the application now? (y/N): "
if /i "%run_now%"=="y" (
    echo.
    echo 🚀 Attempting to start Battery Dashboard...
    call start.bat
)

pause
