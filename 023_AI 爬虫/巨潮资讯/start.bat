@echo off
chcp 65001 >nul
echo ==============================================
echo   CNINFO Announcement Crawler - Starting...
echo ==============================================

echo [1/2] Checking dependencies...
python -c "import flask, flask_cors, requests" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Installing missing packages...
    pip install flask flask-cors requests --no-deps -q 2>nul
    python -c "import flask, flask_cors, requests" 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies. Please run manually:
        echo         pip install --upgrade pip
        echo         pip install flask flask-cors requests
        pause
        exit /b 1
    )
) else (
    echo   All dependencies ready.
)

echo [2/2] Starting server...
echo.
echo Server URL: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

start "" /b python server.py
timeout /t 3 /nobreak >nul
start http://localhost:5000
pause
