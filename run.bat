@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo    Starting ScamRoad AI Road Defect Detection Platform  
echo ========================================================
echo.

set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%scam_road\web\package.json" (
    set "PROJECT_ROOT=%SCRIPT_DIR%scam_road"
) else (
    set "PROJECT_ROOT=%SCRIPT_DIR%"
)
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

echo [INFO] Project directory: %PROJECT_ROOT%

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH! Please install Node.js 18+.
    pause
    exit /b 1
)

REM Ensure web dependencies are installed
if not exist "%PROJECT_ROOT%\web\node_modules" (
    echo [INFO] Installing frontend dependencies in %PROJECT_ROOT%\web...
    pushd "%PROJECT_ROOT%\web"
    call npm install
    popd
)

echo [1/3] Launching FastAPI Backend on http://127.0.0.1:8001...
start "ScamRoad AI Backend" /D "%PROJECT_ROOT%" cmd /k "set PYTHONPATH=. && python scripts\serve_inference.py"

echo [2/3] Launching Vite Frontend on http://127.0.0.1:3000...
start "ScamRoad Web Frontend" /D "%PROJECT_ROOT%\web" cmd /k "npm run dev"

echo [3/3] Opening ScamRoad Overview in browser...
timeout /t 5 /nobreak >nul
start http://127.0.0.1:3000

echo.
echo ========================================================
echo    ScamRoad is now running!
echo    - AI Inference Engine: http://127.0.0.1:8001
echo    - Overview & Showcase:  http://127.0.0.1:3000
echo    - Interactive Scanner:  http://127.0.0.1:3000/scanner
echo    - Audit Report & PDF:   http://127.0.0.1:3000/report
echo ========================================================
