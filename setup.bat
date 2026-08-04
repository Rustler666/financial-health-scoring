@echo off
title Financial Health Scorer - Setup
echo ============================================
echo    Installing dependencies...
echo ============================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)
echo Python found.
echo Installing packages (this may take a few minutes)...
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    python -m pip install -r requirements.txt
)
echo.
echo Setup complete! Now run:  run_auto.bat
echo.
pause
