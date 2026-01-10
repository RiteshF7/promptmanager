@echo off
echo Starting server...
cd /d "%~dp0"

REM Check if server is already running
netstat -ano | findstr :5000 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo Warning: Port 5000 is already in use!
    echo Stopping existing server...
    call stop_server.bat
    timeout /t 1 /nobreak >nul
)

REM Start Python in background using PowerShell to get PID
powershell -Command "$process = Start-Process -FilePath 'python' -ArgumentList 'app.py' -NoNewWindow -PassThru -RedirectStandardOutput 'app.log' -RedirectStandardError 'app.log'; $process.Id | Out-File -FilePath 'app.pid' -Encoding ASCII; Write-Host 'Server started in background. PID:' $process.Id; Write-Host 'Logs are being written to app.log'"

REM Verify the server started by checking the port
timeout /t 2 /nobreak >nul
netstat -ano | findstr :5000 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo Server is running on port 5000
) else (
    echo Warning: Server may not have started properly. Check app.log for errors.
)

