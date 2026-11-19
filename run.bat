@echo off
echo ========================================================
echo    Starting ScamRoad AI Road Defect Detection Platform  
echo ========================================================
echo.

set SCRIPT_DIR=%~dp0
if exist "%SCRIPT_DIR%scam_road" (
    set PROJECT_ROOT=%SCRIPT_DIR%scam_road
) else (
    set PROJECT_ROOT=%SCRIPT_DIR%
)

echo [1/3] Launching FastAPI Backend on http://localhost:8001...
start "ScamRoad AI Backend" cmd /k "cd /d "%PROJECT_ROOT%" && set PYTHONPATH=. && python scripts\serve_inference.py"

echo [2/3] Launching Vite Frontend on http://localhost:3000...
start "ScamRoad Web Frontend" cmd /k "cd /d "%PROJECT_ROOT%\web" && npm run dev"

echo [3/3] Opening ScamRoad Overview in default browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================================
echo    ScamRoad is now running!
echo    - AI Inference Engine: http://localhost:8001
echo    - Overview & Showcase:  http://localhost:3000
echo    - Interactive Scanner:  http://localhost:3000/scanner
echo    - Audit Report & PDF:   http://localhost:3000/report
echo ========================================================
