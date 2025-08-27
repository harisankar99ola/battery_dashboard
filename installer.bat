@echo off
setlocal enabledelayedexpansion
title Battery Dashboard Installer
color 0A

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██            🔋 BATTERY DASHBOARD INSTALLER 🔋                ██
echo ██                                                            ██
echo ██              Quick & Easy Setup for Teams                  ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.

REM Configuration
set "REPO_URL=https://github.com/harisankar99ola/battery_dashboard.git"
set "PROJECT_NAME=battery-dashboard"
set "INSTALL_DIR=%USERPROFILE%\Documents\%PROJECT_NAME%"
set "PYTHON_MIN_VERSION=3.8"

echo 📋 Installation Configuration:
echo    • Repository: %REPO_URL%
echo    • Install Location: %INSTALL_DIR%
echo    • Python Requirement: %PYTHON_MIN_VERSION%+
echo.

REM Check if Git is installed
echo 🔍 Checking prerequisites...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed or not in PATH
    echo.
    echo Please install Git from: https://git-scm.com/download/windows
    echo Then run this installer again.
    echo.
    pause
    exit /b 1
)
echo ✓ Git found

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python %PYTHON_MIN_VERSION%+ from: https://python.org/downloads
    echo Make sure to check 'Add Python to PATH' during installation
    echo Then run this installer again.
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found

REM Check Python version (basic check)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if %MAJOR% LSS 3 (
    echo ❌ Python version too old. Requires Python %PYTHON_MIN_VERSION%+
    pause
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 8 (
    echo ❌ Python version too old. Requires Python %PYTHON_MIN_VERSION%+
    pause
    exit /b 1
)

echo.
echo 🚀 Starting installation process...
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" (
    echo 📁 Creating installation directory...
    mkdir "%INSTALL_DIR%"
    if errorlevel 1 (
        echo ❌ Failed to create installation directory
        pause
        exit /b 1
    )
    echo ✓ Directory created: %INSTALL_DIR%
) else (
    echo ⚠️  Installation directory already exists
    echo.
    set /p "CHOICE=Do you want to reinstall? This will delete existing files. (y/N): "
    if /i "!CHOICE!" NEQ "y" (
        echo Installation cancelled.
        pause
        exit /b 0
    )
    echo 🗑️  Removing existing installation...
    rmdir /s /q "%INSTALL_DIR%"
    mkdir "%INSTALL_DIR%"
)

REM Clone the repository
echo.
echo 📦 Downloading Battery Dashboard from GitHub...
cd /d "%USERPROFILE%\Documents"
git clone "%REPO_URL%" "%PROJECT_NAME%"
if errorlevel 1 (
    echo ❌ Failed to clone repository
    echo Check your internet connection and repository URL
    pause
    exit /b 1
)
echo ✓ Repository cloned successfully

REM Change to project directory
cd /d "%INSTALL_DIR%"

REM Create virtual environment
echo.
echo 🐍 Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

REM Upgrade pip
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✓ Pip upgraded

REM Install requirements
echo 📚 Installing Python dependencies...
echo    This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo Check the error messages above
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully

REM Create Desktop shortcut
echo.
echo 🔗 Creating shortcuts...
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\Battery Dashboard.lnk"
set "BATCH_PATH=%INSTALL_DIR%\start.bat"

REM Create VBS script to create shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > create_shortcut.vbs
echo sLinkFile = "%SHORTCUT_PATH%" >> create_shortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> create_shortcut.vbs
echo oLink.TargetPath = "%BATCH_PATH%" >> create_shortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> create_shortcut.vbs
echo oLink.Description = "Battery Dashboard - Data Analysis Tool" >> create_shortcut.vbs
echo oLink.IconLocation = "shell32.dll,21" >> create_shortcut.vbs
echo oLink.Save >> create_shortcut.vbs

cscript //nologo create_shortcut.vbs
del create_shortcut.vbs

if exist "%SHORTCUT_PATH%" (
    echo ✓ Desktop shortcut created
) else (
    echo ⚠️  Could not create desktop shortcut
)

REM Create Start Menu shortcut
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
copy "%SHORTCUT_PATH%" "%START_MENU%\Battery Dashboard.lnk" >nul 2>&1
if exist "%START_MENU%\Battery Dashboard.lnk" (
    echo ✓ Start Menu shortcut created
)

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██                ✅ INSTALLATION COMPLETE! ✅                ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.

echo 🎉 Battery Dashboard has been successfully installed!
echo.
echo 📍 Installation Location: %INSTALL_DIR%
echo 🖥️  Desktop Shortcut: Battery Dashboard
echo 📱 Start Menu: Battery Dashboard
echo.
echo ⚠️  IMPORTANT NEXT STEPS:
echo.
echo 1. 🔑 SET UP GOOGLE DRIVE CREDENTIALS:
echo    • Run: setup_credentials.bat
echo    • Follow the instructions to set up Google Drive API
echo.
echo 2. 🚀 LAUNCH THE APPLICATION:
echo    • Double-click "Battery Dashboard" on your Desktop
echo    • Or run: start.bat from the installation folder
echo    • Or click Start → Battery Dashboard
echo.
echo 3. 🛑 STOP THE APPLICATION:
echo    • Run: stop.bat to stop all services
echo    • Or press Ctrl+C in the terminal
echo.
echo 4. 🌐 ACCESS THE DASHBOARD:
echo    • Backend API: http://localhost:8000
echo    • Frontend Dashboard: http://localhost:8050
echo    • Browser will open automatically
echo.
echo 📖 For detailed instructions, see README.md in the installation folder
echo.
echo 🆘 Need Help?
echo    • Check README.md for troubleshooting
echo    • Visit: https://github.com/harisankar99ola/battery_dashboard/issues
echo.

set /p "SETUP_CREDS=Do you want to set up Google Drive credentials now? (y/N): "
if /i "!SETUP_CREDS!" EQU "y" (
    echo.
    echo 🔑 Launching credentials setup...
    call setup_credentials.bat
)

echo.
set /p "LAUNCH_NOW=Do you want to launch Battery Dashboard now? (y/N): "
if /i "!LAUNCH_NOW!" EQU "y" (
    echo.
    echo 🚀 Launching Battery Dashboard...
    start "" "%BATCH_PATH%"
    echo ✓ Dashboard launched! Check your browser.
)

echo.
echo 🎊 Installation complete! Enjoy using Battery Dashboard!
echo.
pause
