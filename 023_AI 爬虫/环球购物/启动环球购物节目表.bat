@echo off
title Shark Shopping Program Guide

echo.
echo  ========================================
echo    Shark Shopping Program Guide - Start
echo  ========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found. Please install Python 3.6+
    echo  Download: https://www.python.org/downloads/
    goto :end
)

:: Check files
if not exist "shark_server.py" (
    echo  [ERROR] shark_server.py not found. Please keep it in the same folder.
    goto :end
)
if not exist "shark_shopping_viewer.html" (
    echo  [ERROR] shark_shopping_viewer.html not found. Please keep it in the same folder.
    goto :end
)

:: Check requests
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo  Installing requests...
    pip install requests --quiet
    if %errorlevel% neq 0 (
        echo  [ERROR] Failed to install requests. Run: pip install requests
        goto :end
    )
)

:: Start server
echo  Starting server...
start /b python shark_server.py --port 5000

:: Wait for server
timeout /t 2 /nobreak >nul

:: Open browser
start http://localhost:5000/shark_shopping_viewer.html

echo  [OK] Server started. Browser opened.
echo  URL: http://localhost:5000/shark_shopping_viewer.html
echo  Press Ctrl+C to stop the server.
echo.

:: Keep window open
:loop
timeout /t 60 /nobreak >nul
goto loop

:end
echo.
pause
