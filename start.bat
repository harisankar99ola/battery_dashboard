@echo off
echo.
echo ===============================================
echo 🔋 BATTERY DATA DASHBOARD LAUNCHER
echo ===============================================
echo.

REM Get the directory where this script is located
set DASHBOARD_DIR=%~dp0
cd /d "%DASHBOARD_DIR%"

REM Kill any existing Python processes to avoid port conflicts
echo 🧹 Cleaning up existing processes...
taskkill /f /im python.exe >nul 2>&1

REM Check if Python is installed
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    echo.
    pause
    exit /b 1
)
python --version
echo ✅ Python detected

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        echo.
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment for dependency installation
echo.
echo 🔧 Setting up dependencies...
call venv\Scripts\activate.bat

REM Install backend dependencies
echo 📥 Installing backend dependencies...
cd backend
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Failed to install backend dependencies
    echo.
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed

REM Install frontend dependencies
echo 📥 Installing frontend dependencies...
cd ..\frontend
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Failed to install frontend dependencies
    echo.
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed

REM Go back to main directory
cd "%DASHBOARD_DIR%"

echo.
echo 🚀 Starting services...

REM Start backend server in a new window that stays open
start "Battery Dashboard API" /min cmd /c "cd /d "%DASHBOARD_DIR%" && call venv\Scripts\activate.bat && cd backend && echo Starting Backend API... && uvicorn main_simple:app --host 0.0.0.0 --port 8000 && pause"

REM Wait for backend to start
echo ⏳ Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

REM Start frontend in a new window that stays open
start "Battery Dashboard Frontend" /min cmd /c "cd /d "%DASHBOARD_DIR%" && call venv\Scripts\activate.bat && cd frontend && echo Starting Frontend Dashboard... && python app.py && pause"

REM Wait for frontend to start
echo ⏳ Waiting for frontend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo ===============================================
echo ✨ DASHBOARD IS READY!
echo ===============================================
echo.
echo 📊 Dashboard URL: http://localhost:8050
echo 🔌 API Documentation: http://localhost:8000/docs
echo.
echo The dashboard is running in separate windows.
echo Close those windows to stop the services.
echo.
echo Opening dashboard in your default browser...
timeout /t 2 /nobreak >nul
start http://localhost:8050

echo.
echo Press any key to exit this launcher...
pause >nul

echo.
echo Dashboard is still running in background windows.
echo Close the API and Frontend windows to stop the services.
echo.
