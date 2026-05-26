@echo off
chcp 65001 >nul
echo ========================================
echo GuoJi Report Crawler System
echo ========================================
echo.

echo [1/3] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)
echo Python OK

echo.
echo [2/3] Installing dependencies...
pip install flask flask-cors requests beautifulsoup4 pillow img2pdf >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install
    echo Trying to continue...
)
echo Dependencies OK

echo.
echo [3/3] Starting server...
echo.
echo ========================================
echo Server is starting...
echo Please wait for the browser to open...
echo ========================================
echo.

start /b python app.py

timeout /t 3 /nobreak >nul

echo Opening browser...
start http://localhost:5001

echo.
echo ========================================
echo Server is running at http://localhost:5001
echo Press Ctrl+C to stop the server
echo ========================================
echo.

pause
