@echo off
chcp 65001 >nul
title 财务健康度评估系统 - 交互运行
color 0E

echo ================================================
echo   上市公司财务健康度评估系统 - 交互模式
echo ================================================
echo.
echo 此模式会逐步引导你完成数据获取和报告生成。
echo 如果已有数据文件，可以选择跳过重新获取。
echo.

python main.py

echo.
echo ================================================
echo   运行结束！
echo ================================================
echo.
echo 请打开 reports\financial_health_report.html 查看报告
echo.
pause
