@echo off
chcp 65001 >nul 2>&1
title CBNData Report Center

echo ============================================
echo   CBNData Report Center - Starting...
echo ============================================
echo.

:: Install dependencies
echo Checking dependencies...
pip install -r requirements.txt --quiet 2>nul
if %errorlevel% neq 0 (
    echo [WARN] Failed to install some dependencies, trying anyway...
)
echo.

:: Start Flask server in background
start /b python app.py

:: Wait for server to be ready
echo Waiting for server to start...
timeout /t 3 /nobreak >nul

:: Open browser
echo Opening browser...
start http://localhost:5000

echo.
echo ============================================
echo   Server is running at http://localhost:5000
echo   Press Ctrl+C to stop the server
echo ============================================
echo.

:: Keep the window open
python -c "import time; [time.sleep(1)] while True" 2>nul
