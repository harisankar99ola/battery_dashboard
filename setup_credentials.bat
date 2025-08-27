@echo off
title Battery Dashboard - Credentials Setup
echo.
echo ============================================
echo    Battery Dashboard - Credentials Setup
echo ============================================
echo.

REM Check if credentials.json exists
if exist "credentials.json" (
    echo ✓ credentials.json found
    goto :check_token
) else (
    echo ✗ credentials.json NOT found
    echo.
    echo SETUP REQUIRED:
    echo 1. Go to Google Cloud Console: https://console.cloud.google.com/
    echo 2. Create a new project or select existing one
    echo 3. Enable Google Drive API
    echo 4. Create OAuth 2.0 credentials for Desktop application
    echo 5. Download the JSON file
    echo 6. Rename it to 'credentials.json' and place in this folder
    echo.
    echo After setting up credentials.json, run this script again.
    echo.
    pause
    exit /b 1
)

:check_token
if exist "token.json" (
    echo ✓ token.json found - Authentication already completed
    echo.
    echo Your Google Drive authentication is ready!
    echo You can now run the application with: python src\main.py
) else (
    echo ✗ token.json NOT found
    echo.
    echo First-time authentication will be required.
    echo When you run the application, a browser will open for Google authentication.
    echo.
    echo Ready to proceed with authentication on first run.
)

echo.
echo ============================================
echo            Credentials Status
echo ============================================
if exist "credentials.json" (
    echo ✓ Google API Credentials: READY
) else (
    echo ✗ Google API Credentials: MISSING
)

if exist "token.json" (
    echo ✓ Authentication Token: READY
) else (
    echo ⚠ Authentication Token: WILL BE CREATED ON FIRST RUN
)

echo.
echo ============================================
echo              Next Steps
echo ============================================
echo.
if exist "credentials.json" (
    echo 1. Run the application: python src\main.py
    echo 2. If first time, complete Google authentication in browser
    echo 3. Dashboard will open at http://localhost:8050
) else (
    echo 1. Set up credentials.json as described above
    echo 2. Run this script again to verify setup
    echo 3. Then run: python src\main.py
)

echo.
pause
