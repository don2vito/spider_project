@echo off
title Happigo TV5 Schedule

echo.
echo  Starting server...
echo.

start "" /b python "%~dp0server.py"
timeout /t 2 /nobreak >nul

start http://localhost:8080/happigo_schedule.html

echo  Server started. Browser opened.
echo  Close this window to stop the server.
echo.
pause >nul
taskkill /f /im python.exe >nul 2>&1
