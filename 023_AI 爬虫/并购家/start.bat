@echo off
chcp 65001 >nul 2>&1
title IPOIPO Report Scraper

echo ============================================
echo   IPOIPO Industry Report Scraper
echo   Starting server...
echo ============================================
echo.

:: Upgrade pip first
python -m pip install --upgrade pip --quiet 2>nul

:: Install/upgrade dependencies
pip install "flask>=2.3.0" "Jinja2>=3.1.0" "markupsafe>=2.1.0" "requests>=2.28.0" "beautifulsoup4>=4.12.0" "lxml>=4.9.0" "DrissionPage>=4.0.0" "selenium>=4.10.0" --quiet 2>nul

:: Start the Flask server in a new process
start /b python server.py

:: Wait for server to be ready
echo Waiting for server to start...
timeout /t 3 /nobreak >nul

:: Open browser
start http://localhost:5000

echo.
echo Server is running at http://localhost:5000
echo Press Ctrl+C to stop the server.
echo.

:: Keep the window open
python -c "import time; [time.sleep(1)] while True" 2>nul
