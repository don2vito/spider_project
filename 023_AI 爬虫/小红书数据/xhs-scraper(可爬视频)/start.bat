@echo off
chcp 65001 >nul 2>&1
title XHS Data Scraper - Starting...
color 0F

echo ============================================================
echo   XHS Data Scraper - One-Click Launcher (v2.0)
echo   Browser-assisted signing via Playwright
echo ============================================================
echo.

:: Check Python installation
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    goto :end
)

echo [INFO] Python found:
python --version
echo.

:: Install Python dependencies
echo [INFO] Installing Python dependencies...
call pip install --upgrade fastapi "uvicorn[standard]" httpx pandas >nul 2>&1
echo [INFO] Python dependencies ready.
echo.

:: Install Playwright
echo [INFO] Checking Playwright...
python -c "from playwright.async_api import async_playwright" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing Playwright...
    call pip install --upgrade playwright >nul 2>&1
    echo [INFO] Playwright installed.
)
echo [INFO] Playwright ready.
echo.

:: Install Chromium browser
echo [INFO] Checking Chromium browser...
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Chromium not found or broken. Installing...
    echo [INFO] This may take a few minutes on first run, please wait...
    call python -m playwright install chromium
    if %errorlevel% neq 0 (
        echo [WARN] Chromium install may have failed. Will retry during server startup.
    ) else (
        echo [INFO] Chromium installed successfully.
    )
) else (
    echo [INFO] Chromium browser ready.
)
echo.

:: Start server
echo [INFO] Starting server on http://localhost:8080
echo [INFO] Press Ctrl+C to stop the server.
echo ============================================================
echo.

start "" http://localhost:8080

python server.py

:end
echo.
echo ============================================================
echo   Server stopped. Press any key to close this window.
echo ============================================================
pause >nul
