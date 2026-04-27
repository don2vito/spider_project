@echo off
chcp 65001 >nul
title National Bureau of Statistics - Monthly Data Viewer

echo ============================================
echo   National Bureau of Statistics
echo   Monthly Data Viewer - Launcher
echo ============================================
echo.

:: Check Python installation
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

:: Install dependencies if needed
echo [INFO] Checking dependencies...
pip install -r requirements.txt --quiet 2>nul
if %errorlevel% neq 0 (
    echo [WARN] Failed to install some dependencies, attempting to continue anyway...
)

echo [INFO] Starting proxy server on http://localhost:5000 ...
echo.

:: Start Flask server in background
start /b python app.py

:: Wait for server to be ready
echo [INFO] Waiting for server to start...
timeout /t 4 /nobreak >nul

:: Open browser
echo [INFO] Launching browser...
start "" viewer.html

echo.
echo ============================================
echo   Server is running at http://localhost:5000
echo   Close this window to stop the server.
echo ============================================
echo.

:: Block so the server keeps running
cmd /k
