@echo off
setlocal

REM ─────────────────────────────────────────────────────────────────────────────
REM  Configuration: adjust these if you moved things around

set BASE_DIR=%~dp0

set BACKEND_DIR=%BASE_DIR%\chatbot\backend
set FRONTEND_DIR=%BASE_DIR%\chatbot\frontend

set BACKEND_CMD=python main.py
set FRONTEND_INSTALL_CMD=npm install
set FRONTEND_CMD=npm run dev

REM Ports and URLs
set BACKEND_PORT=5000
set FRONTEND_URL=http://localhost:5173

REM ─────────────────────────────────────────────────────────────────────────────
echo Launching UB Chatbot prototype...
echo.

REM Start backend in a new window
start "UB Chatbot Backend" cmd /k ^
    "cd /d "%BACKEND_DIR%" && %BACKEND_CMD%"

REM Wait for backend to be up (poll port %BACKEND_PORT%)
echo Waiting for backend to start on port %BACKEND_PORT%...
:WAIT_BACKEND
powershell -Command "if ((Test-NetConnection -ComputerName 'localhost' -Port %BACKEND_PORT%).TcpTestSucceeded) { exit 0 } else { exit 1 }"
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto WAIT_BACKEND
)
echo Backend is up!

REM Install frontend dependencies first
echo Installing frontend dependencies...
cd /d "%FRONTEND_DIR%"
call %FRONTEND_INSTALL_CMD%

REM Now start frontend

start "UB Chatbot Frontend" cmd /k ^
    "cd /d "%FRONTEND_DIR%" && %FRONTEND_CMD%"

REM Give frontend a moment to spin up, then open browser
timeout /t 5 /nobreak >nul
echo Opening browser at %FRONTEND_URL%...
start "" "%FRONTEND_URL%"

echo.
echo Both services are running.
echo Press Q then ENTER here to stop both.

:WAIT_INPUT
set /p choice=Enter choice: 
if /i "%choice%"=="Q" goto SHUTDOWN
echo Invalid choice. Press Q to quit. & goto WAIT_INPUT

:SHUTDOWN
echo Shutting down...
REM Kill the backend and frontend windows by title
taskkill /FI "WINDOWTITLE eq UB Chatbot Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq UB Chatbot Frontend*" /T /F >nul 2>&1
echo All processes terminated.
endlocal
exit /b
