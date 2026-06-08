#!/bin/bash
# -*- coding: utf-8 -*-
#
# 供应商不良行为查询工具 - 国产Linux系统启动脚本
#

# 确保中文显示
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

echo "========================================"
echo "  供应商不良行为查询工具 - Linux启动脚本"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装"
    echo "Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "银河麒麟/统信UOS: 请使用系统软件中心安装"
    read -p "按回车键退出..."
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "[错误] 未检测到pip3，请先安装"
    echo "Ubuntu/Debian: sudo apt-get install python3-pip"
    read -p "按回车键退出..."
    exit 1
fi

# 安装系统依赖（适用于Debian系Linux）
install_dependencies() {
    echo "[提示] 正在检查系统依赖..."

    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu/统信UOS/银河麒麟可能基于Debian
        echo "[信息] 尝试安装系统依赖..."
        sudo apt-get update
        sudo apt-get install -y python3-tk python3-pil python3-pil.imagetk
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL/中标麒麟可能使用yum
        echo "[信息] 使用yum安装系统依赖..."
        sudo yum install -y python3-tkinter python3-pillow
    elif command -v dnf &> /dev/null; then
        # Fedora
        echo "[信息] 使用dnf安装系统依赖..."
        sudo dnf install -y python3-tkinter python3-pillow
    fi
}

# 检查Tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[警告] Tkinter未安装或配置不正确"
    install_dependencies
fi

# 安装Python依赖
echo "[1/4] 检查Python依赖..."
pip3 install -r requirements.txt --quiet 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[2/4] 安装Python依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        read -p "按回车键退出..."
        exit 1
    fi
fi

# 安装Playwright浏览器
echo "[3/4] 检查浏览器..."
if ! python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "[提示] 首次运行需要安装浏览器引擎..."
    playwright install chromium 2>/dev/null || playwright install firefox 2>/dev/null
fi

# 启动应用
echo "[4/4] 启动应用..."
echo ""
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 程序异常退出"
    read -p "按回车键退出..."
fi