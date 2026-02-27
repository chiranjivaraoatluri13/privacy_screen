@REM Camera Access Privacy Protection - Background Mode (Headless)
@REM This batch script runs the application in background mode with no window display
@REM Results are logged to logs/ directory

@echo off
setlocal enabledelayedexpansion

echo.
echo ========== CAMERA ACCESS PRIVACY PROTECTION (HEADLESS MODE) ==========
echo.
echo - Running in BACKGROUND (no window)
echo - Face detection and blur working silently
echo - Press Ctrl+C to stop
echo - Check logs/ folder for session data
echo.

REM Check if venv exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

echo Launching application (background mode)...
echo.

REM Run main.py with headless mode
python src/main.py

REM Deactivate venv on exit
deactivate

echo.
echo Application stopped. Check logs/ for details.
pause
