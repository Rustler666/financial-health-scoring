@echo off
chcp 65001 >nul
title 财务健康度评估系统 - 一键生成报告
color 0B

echo ================================================
echo   上市公司财务健康度评估系统 - 自动模式
echo ================================================
echo.
echo 正在使用已有数据一键生成报告...
echo.

python main.py --auto

echo.
if exist reports\financial_health_report.html (
    echo ================================================
    echo   报告生成成功！
    echo ================================================
    echo.
    echo 正在打开报告...
    start reports\financial_health_report.html
) else (
    echo [错误] 报告未生成，请检查数据文件是否存在。
)
echo.
pause
