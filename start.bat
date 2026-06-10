@echo off
setlocal

set ROOT=%~dp0
if "%ROOT:~-1%"=="\" set ROOT=%ROOT:~0,-1%

set BACKEND=%ROOT%\backend
set FRONTEND=%ROOT%\frontend
set VENV=%BACKEND%\.venv

echo ========================================
echo   Scout - Competitive Analysis Workbench
echo ========================================
echo.

echo [1/3] Starting Backend (FastAPI :8000)
if not exist "%VENV%\Scripts\python.exe" (
    echo   [setup] creating virtualenv...
    python -m venv "%VENV%"
    if errorlevel 1 (
        echo   [ERROR] failed to create venv. Is python installed?
        pause
        exit /b 1
    )
    echo   [setup] installing dependencies...
    "%VENV%\Scripts\pip" install -r "%BACKEND%\requirements.txt" --quiet
    if errorlevel 1 (
        echo   [ERROR] pip install failed
        pause
        exit /b 1
    )
) else (
    echo   [ok] venv exists, skipping install
)

start "Scout Backend" cmd /k "cd /d %BACKEND% && .venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo [2/3] Starting Frontend (Vite :5003)
if not exist "%FRONTEND%\node_modules" (
    echo   [setup] installing npm packages...
    pushd "%FRONTEND%"
    call npm install --silent
    popd
) else (
    echo   [ok] node_modules exists, skipping install
)

start "Scout Frontend" cmd /k "cd /d %FRONTEND% && npm run dev"

echo [3/3] Waiting for services, then opening browser...
timeout /t 6 /nobreak >nul
start "" "http://localhost:5003"

echo.
echo ========================================
echo   Backend  :  http://127.0.0.1:8000
echo   Frontend :  http://localhost:5003
echo   API docs :  http://127.0.0.1:8000/docs
echo ========================================
echo.
echo Two service windows opened. Closing this window is safe.
echo.
pause
endlocal
