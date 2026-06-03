@echo off
echo ========================================
echo   DeepSeek Neural Interface
echo   Starting server...
echo ========================================
echo.

cd /d "%~dp0"

REM Check if Python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt -q
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting Flask server on http://localhost:8080
echo Press Ctrl+C to stop
echo.
python server.py

pause
