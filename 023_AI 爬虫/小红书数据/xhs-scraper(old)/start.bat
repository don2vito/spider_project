@echo off
chcp 65001 >nul
title XHS Data Scraper

echo ========================================
echo   XHS Data Scraper - Starting...
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8+ first.
    echo         Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Step 1: Install dependencies
echo [1/5] Checking dependencies...
pip install -r requirements.txt -q --break-system-packages 2>nul
if errorlevel 1 (
    pip install -r requirements.txt -q 2>nul
)
echo       Dependencies installed.

:: Step 2: Check stealth.min.js
echo [2/5] Checking stealth.min.js...
if not exist "stealth.min.js" (
    echo       Downloading stealth.min.js...
    curl -sL -o stealth.min.js "https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js"
    if errorlevel 1 (
        echo       [WARN] Failed to download stealth.min.js, signing may not work optimally.
    ) else (
        echo       stealth.min.js downloaded.
    )
) else (
    echo       stealth.min.js found.
)

:: Step 3: Check Playwright browser
echo [3/5] Checking Playwright browser...
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop()" >nul 2>&1
if errorlevel 1 (
    echo       Installing Playwright Chromium browser...
    python -m playwright install chromium
    if errorlevel 1 (
        echo       [WARN] Playwright browser installation may have failed.
    )
) else (
    echo       Playwright browser ready.
)

:: Step 4: Start sign server (background)
echo [4/5] Starting sign server on port 5005...
start /b python sign_server.py >nul 2>&1
echo       Waiting for sign server to initialize...
timeout /t 10 /nobreak >nul

:: Step 5: Start main API server
echo [5/5] Starting main server on port 8000...
start /b python -m uvicorn app:app --host 0.0.0.0 --port 8000 >nul 2>&1
timeout /t 3 /nobreak >nul

:: Open browser
echo.
echo ========================================
echo   XHS Data Scraper is running!
echo   Sign Server:  http://localhost:5005
echo   Main Server:  http://localhost:8000
echo ========================================
echo.
echo   Opening browser...
start http://localhost:8000

echo.
echo   [Press Ctrl+C to stop all servers]
echo.

:: Keep window open
pause >nul
