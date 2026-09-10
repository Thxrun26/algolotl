@echo off
REM ============================================================
REM  Algolotl - Windows one-click launcher
REM  Double-click this file (place it in the algolotl-pkg root)
REM ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo   ========================================
echo    Algolotl - starting up...
echo   ========================================
echo.

REM ---- 1. Find Python (prefer 'py', fall back to 'python') ----
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY (
    where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo [ERROR] Python was not found on PATH.
    echo         Install Python 3.10+ from https://www.python.org/downloads/
    echo         and tick "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo [1/5] Using Python: %PY%
%PY% --version

REM ---- 2. Generate the problem dataset ----
echo.
echo [2/5] Building dataset...
%PY% scripts\generate.py
if errorlevel 1 (
    echo [ERROR] Dataset generation failed. See the message above.
    pause
    exit /b 1
)

REM ---- 3. Create a virtual environment (once) ----
echo.
echo [3/5] Preparing virtual environment...
if not exist "backend\.venv" (
    %PY% -m venv backend\.venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        pause
        exit /b 1
    )
)

REM ---- 4. Install dependencies ----
echo.
echo [4/5] Installing dependencies (first run may take a minute)...
call "backend\.venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
call "backend\.venv\Scripts\python.exe" -m pip install --quiet -r backend\requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency install failed.
    pause
    exit /b 1
)

REM ---- 5. Generate a session secret and start the server ----
echo.
echo [5/5] Starting server...
for /f "delims=" %%i in ('"backend\.venv\Scripts\python.exe" -c "import secrets;print(secrets.token_hex(32))"') do set "ALGO_SECRET_KEY=%%i"

echo.
echo   ========================================
echo    Algolotl is running!
echo    Open:  http://localhost:8000
echo    Docs:  http://localhost:8000/docs
echo    (Press Ctrl+C in this window to stop)
echo   ========================================
echo.

REM Open the browser automatically after a short delay
start "" http://localhost:8000

cd backend
call ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

echo.
echo Server stopped.
pause
