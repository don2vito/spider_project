@echo off
chcp 65001 >nul
title Weather History Scraper

echo ============================================
echo   Weather History Data Scraper
echo   tianqihoubao.com
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

:: Install dependencies
echo [INFO] Checking and installing dependencies...
pip install flask requests beautifulsoup4 openpyxl --quiet --break-system-packages 2>nul
if errorlevel 1 (
    pip install flask requests beautifulsoup4 openpyxl --quiet 2>nul
)
echo [INFO] Dependencies ready.
echo.

:: Create cache directory
if not exist "cache" mkdir cache

:: Start server and open browser
echo [INFO] Starting server on http://127.0.0.1:5000
echo [INFO] Press Ctrl+C to stop the server.
echo.
start "" "http://127.0.0.1:5000"
python app.py

pause
