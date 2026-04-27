@echo off
chcp 65001 >nul
title Shanghai Statistics Data Scraper

echo ============================================================
echo   Shanghai Statistics Data Scraper
echo   Starting server...
echo ============================================================

:: Install dependencies if needed
pip install flask flask-cors requests beautifulsoup4 xlrd openpyxl --break-system-packages >nul 2>&1

:: Start the server in background and open browser
start "" python "%~dp0server.py"
timeout /t 3 /nobreak >nul
start http://localhost:5000

echo.
echo   Server is running at http://localhost:5000
echo   Press Ctrl+C in the server window to stop.
echo ============================================================
