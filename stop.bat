@echo off
title Battery Dashboard - Stop Services
echo.
echo ===============================================
echo 🛑 STOPPING BATTERY DASHBOARD SERVICES
echo ===============================================
echo.

echo 🔍 Checking for running services...
echo.

REM Check if any Python processes are running
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul
if %errorlevel% equ 0 (
    echo 🐍 Found Python processes, stopping...
    taskkill /f /im python.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Python processes stopped
    ) else (
        echo ⚠️  Some Python processes may still be running
    )
) else (
    echo ℹ️  No Python processes found
)

REM Check if any uvicorn processes are running
tasklist /fi "imagename eq uvicorn.exe" 2>nul | find /i "uvicorn.exe" >nul
if %errorlevel% equ 0 (
    echo 🌐 Found uvicorn processes, stopping...
    taskkill /f /im uvicorn.exe >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Uvicorn processes stopped
    ) else (
        echo ⚠️  Some uvicorn processes may still be running
    )
) else (
    echo ℹ️  No uvicorn processes found
)

REM Check ports
echo.
echo 🔌 Checking if ports are free...
netstat -an | find "LISTENING" | find ":8000" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Port 8000 still in use
) else (
    echo ✅ Port 8000 is free
)

netstat -an | find "LISTENING" | find ":8050" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Port 8050 still in use
) else (
    echo ✅ Port 8050 is free
)

echo.
echo ===============================================
echo ✅ BATTERY DASHBOARD SERVICES STOPPED
echo ===============================================
echo.
echo You can now run start.bat to restart the dashboard
echo.
pause
