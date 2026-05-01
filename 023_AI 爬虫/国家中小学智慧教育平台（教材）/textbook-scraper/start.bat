@echo off
chcp 65001 >nul
title Electronic Textbook Downloader

echo ============================================
echo   Electronic Textbook Downloader
echo ============================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

:: Install dependencies if needed
echo [INFO] Checking dependencies...
pip install flask requests -q 2>nul
echo [INFO] Dependencies ready.
echo.

:: Get script directory and change to it
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Start server in background
echo [INFO] Starting server...
start /b python server.py

:: Wait for server to be ready
echo [INFO] Waiting for server to start...
timeout /t 4 /nobreak >nul

:: Open browser
echo [INFO] Opening browser...
start http://127.0.0.1:5000

echo.
echo ============================================
echo   Server is running at http://127.0.0.1:5000
echo   Close this window to stop the server.
echo ============================================
echo.
pause >nul
