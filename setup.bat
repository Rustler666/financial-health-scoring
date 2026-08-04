@echo off
chcp 65001 >nul
title 财务健康度评估系统 - 一键安装
color 0A

echo ================================================
echo   上市公司财务健康度评估系统 - 环境安装
echo ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！
    echo.
    echo 请先安装 Python 3.9 或更高版本：
    echo   1. 访问 https://www.python.org/downloads/
    echo   2. 下载并安装 Python 3.9+（勾选 "Add Python to PATH"）
    echo   3. 安装完成后重新运行本脚本
    echo.
    pause
    exit /b 1
)

echo [1/3] Python 已安装：
python --version
echo.

echo [2/3] 检查 pip ...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [错误] pip 未安装，尝试自动安装...
    python -m ensurepip --upgrade
)
echo pip 已就绪
echo.

echo [3/3] 安装项目依赖（akshare, pandas, matplotlib, seaborn）...
echo 这可能需要几分钟，请耐心等待...
echo.
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo.
    echo [警告] 清华源安装失败，尝试默认源...
    python -m pip install -r requirements.txt
)

echo.
echo ================================================
echo   环境安装完成！
echo ================================================
echo.
echo 现在可以运行项目了：
echo   方式1：双击 run.bat  （交互模式）
echo   方式2：双击 run_auto.bat  （一键生成报告）
echo.
pause
