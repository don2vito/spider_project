@echo off
title Huimai TV Schedule

echo.
echo  ========================================
echo   Huimai TV Schedule - Quick Start
echo  ========================================
echo.

:: Start proxy server in new window
start "Huimai Server" python "%~dp0huimai_server.py"

:: Wait for server ready
ping 127.0.0.1 -n 3 >nul

:: Open frontend page
start http://localhost:8765/huimai_tvlist.html

echo  Server started. Browser opened.
echo  Close this window anytime. To stop server, close the "Huimai Server" window.
echo.
pause
