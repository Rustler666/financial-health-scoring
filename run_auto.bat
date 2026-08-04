@echo off
title Financial Health Scorer - Auto Mode
echo ============================================
echo    Financial Health Scoring System
echo    Auto Mode - One-click Report
echo ============================================
echo.
echo Running python main.py --auto ...
echo.
python main.py --auto
echo.
if exist reports\financial_health_report.html (
    echo Report generated successfully!
    echo Opening report in browser...
    start reports\financial_health_report.html
) else (
    echo ERROR: Report not generated.
)
echo.
pause
