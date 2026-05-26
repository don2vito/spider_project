@echo off
echo ========================================
echo  ZhiZhuan100 Data Report Crawler
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo Python OK.

echo.
echo [2/3] Installing dependencies...
pip install flask requests beautifulsoup4 >nul 2>&1
echo Dependencies OK.

echo.
echo [3/3] Starting proxy server...
start /b python "%~dp0server.py"

echo.
echo Waiting for server to start...
:wait_loop
timeout /t 1 /nobreak >nul
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% neq 0 goto wait_loop

echo Server is ready!
echo.
echo Opening browser...
start http://localhost:5000

echo.
echo ========================================
echo  Server is running at http://localhost:5000
echo  Press Ctrl+C to stop the server.
echo ========================================
echo.

pause
