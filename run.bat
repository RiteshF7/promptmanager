@echo off
chcp 65001 >nul
title Prompt Manager - Server Control

:menu
cls
echo.
echo ========================================
echo   Prompt Manager - Server Control
echo ========================================
echo.
echo   [1] Start Server
echo   [2] Restart Server
echo   [3] Stop Server
echo   [4] Check Status
echo   [5] Exit
echo.
echo ========================================
set /p choice="Select an option (1-5): "

if "%choice%"=="1" goto start_server
if "%choice%"=="2" goto restart_server
if "%choice%"=="3" goto stop_server
if "%choice%"=="4" goto check_status
if "%choice%"=="5" goto exit
goto menu

:start_server
cls
echo.
echo ========================================
echo   Starting Prompt Manager Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    echo.
    pause
    goto menu
)

echo [1/3] Checking Python installation...
python --version
echo.

REM Check if server is already running
netstat -ano | findstr :5000 >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 5000 is already in use!
    echo The server may already be running.
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" goto menu
)

echo [2/3] Installing/Updating dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo.
    pause
    goto menu
)
echo Dependencies installed successfully!
echo.

echo [3/3] Starting Flask application...
echo.
echo ========================================
echo   Server will be available at:
echo   http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run the Flask application
python app.py

echo.
echo Server stopped.
pause
goto menu

:restart_server
cls
echo.
echo ========================================
echo   Restarting Prompt Manager Server
echo ========================================
echo.

echo [1/2] Stopping existing server...
call :stop_server_silent
timeout /t 2 /nobreak >nul

echo [2/2] Starting server...
timeout /t 1 /nobreak >nul
goto start_server

:stop_server
cls
echo.
echo ========================================
echo   Stopping Prompt Manager Server
echo ========================================
echo.

call :stop_server_silent

echo.
echo Server stopped successfully!
echo.
pause
goto menu

:stop_server_silent
setlocal enabledelayedexpansion
REM Find and kill Python processes running app.py
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    set pid=%%a
    taskkill /F /PID !pid! >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Stopped process with PID !pid!
    )
)

REM Also try to kill by process name (alternative method)
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr python.exe') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr app.py >nul
    if not errorlevel 1 (
        taskkill /F /PID %%a >nul 2>&1
        echo [OK] Stopped Python process running app.py
    )
)

REM Check if port is still in use
timeout /t 1 /nobreak >nul
netstat -ano | findstr :5000 >nul 2>&1
if errorlevel 1 (
    echo [OK] Port 5000 is now free
) else (
    echo [WARNING] Port 5000 may still be in use
)
endlocal
exit /b

:check_status
cls
echo.
echo ========================================
echo   Server Status Check
echo ========================================
echo.

REM Check if port 5000 is in use
netstat -ano | findstr :5000 >nul 2>&1
if not errorlevel 1 (
    echo [STATUS] Server appears to be RUNNING
    echo.
    echo Active connections on port 5000:
    netstat -ano | findstr :5000
    echo.
    
    REM Try to connect to the server
    python -c "import requests; r = requests.get('http://localhost:5000', timeout=2); print('[OK] Server is responding!')" 2>nul
    if errorlevel 1 (
        echo [WARNING] Server may not be responding correctly
    )
) else (
    echo [STATUS] Server appears to be STOPPED
    echo Port 5000 is not in use
)

echo.
pause
goto menu

:exit
cls
echo.
echo Thank you for using Prompt Manager!
echo.
timeout /t 2 /nobreak >nul
exit
