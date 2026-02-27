@REM Camera Access Privacy Protection - Display Mode (Testing)
@REM This batch script runs the application WITH a live display window for testing
@REM Use this to see the camera feed and face detection in real-time

@echo off
setlocal enabledelayedexpansion

echo.
echo ========== CAMERA ACCESS PRIVACY PROTECTION (DISPLAY MODE) ==========
echo.
echo - Running WITH window display
echo - See live camera feed and face blur
echo - Press 'q' in window or Ctrl+C to stop
echo - Press 'd' to toggle demo overlay
echo - Press 's' to toggle annotations
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

REM Temporarily modify config.json to enable display
echo Launching application (display mode)...
echo.

REM Use Python to temporarily enable headless=false
python -c "import json; cfg=json.load(open('config.json')); cfg['ui']['headless']=False; json.dump(cfg,open('config.json','w'),indent=2)"

REM Run main.py
python src/main.py

REM Restore headless=true
python -c "import json; cfg=json.load(open('config.json')); cfg['ui']['headless']=True; json.dump(cfg,open('config.json','w'),indent=2)"

REM Deactivate venv on exit
deactivate

echo.
echo Application closed. Display mode ended.
pause
