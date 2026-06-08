@echo off
chcp 65001 >nul
echo ========================================
echo   供应商不良行为查询工具 - Windows启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM 检查依赖
echo [1/4] 检查依赖...
pip show playwright >nul 2>&1
if errorlevel 1 (
    echo [2/4] 安装Python依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

REM 安装Playwright浏览器
echo [3/4] 检查浏览器...
python -c "from playwright.sync_api import sync_playwright" >nul 2>&1
if errorlevel 1 (
    echo [提示] 首次运行需要安装浏览器引擎...
    playwright install chromium
)

REM 启动应用
echo [4/4] 启动应用...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    pause
)