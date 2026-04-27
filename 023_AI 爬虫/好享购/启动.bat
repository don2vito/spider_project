@echo off
chcp 65001 >nul
title Happigo Schedule - Launcher

echo.
echo ========================================
echo   Happigo Schedule - Quick Launch
echo ========================================
echo.

:: Start proxy server (current directory)
start /b python "%~dp0server.py"

:: Wait for server to start
timeout /t 2 /nobreak >nul

:: Open browser
start http://localhost:8080/happigo.html

echo.
echo   Server started, browser opened.
echo   Close this window to stop the server.
echo.
echo ========================================

:: Keep window open (press Ctrl+C to stop)
python -c "import time; [time.sleep(1)]"
