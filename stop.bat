@echo off
echo.
echo ===============================================
echo 🛑 STOPPING BATTERY DASHBOARD SERVICES
echo ===============================================
echo.

echo 🧹 Stopping all Python processes...
taskkill /f /im python.exe >nul 2>&1

echo 🧹 Stopping any remaining uvicorn processes...
taskkill /f /im uvicorn.exe >nul 2>&1

echo ✅ All dashboard services have been stopped.
echo.
pause
