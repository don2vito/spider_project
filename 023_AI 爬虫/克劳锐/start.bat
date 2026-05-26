@echo off
title Topklout Report Crawler Server
echo ========================================
echo  Topklout Report Crawler - Launcher
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python detected.

REM Install required dependencies
echo.
echo [INFO] Installing dependencies...
pip install flask flask-cors requests beautifulsoup4 pillow playwright >nul 2>&1
if errorlevel 1 (
    echo [WARN] Some dependencies may have failed to install. Trying with verbose output...
    pip install flask flask-cors requests beautifulsoup4 pillow playwright
)

REM Install Playwright browser
echo.
echo [INFO] Checking Playwright browser...
python -m playwright install chromium >nul 2>&1
if errorlevel 1 (
    echo [WARN] Playwright browser install may have issues. The server will use fallback layers.
)

echo.
echo [INFO] Starting server on port 5001...
echo [INFO] The browser will open automatically.
echo.

REM Open browser after a short delay
start "" cmd /c "timeout /t 3 >nul && start http://localhost:5001"

REM Start the Flask server
python app.py

pause
