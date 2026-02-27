@REM Camera Access - Enrollment Launcher
@REM This batch script launches the face enrollment routine

@echo off
setlocal enabledelayedexpansion

echo.
echo ========== FACE ENROLLMENT ROUTINE ==========
echo.
echo This will create a template of your face for verification.
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

echo.
echo Launching enrollment...
echo.

REM Run enroll.py
python enroll.py

REM Deactivate venv on exit
deactivate

echo.
echo Enrollment complete.
pause
