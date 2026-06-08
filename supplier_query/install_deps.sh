#!/bin/bash
# -*- coding: utf-8 -*-
#
# 国产系统依赖一键安装脚本
# 适用于: 统信UOS、银河麒麟、中标麒麟
#

set -e

echo "========================================"
echo "  国产系统依赖一键安装脚本"
echo "========================================"
echo ""

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$NAME
        OS_VERSION=$VERSION_ID
    elif command -v uname &> /dev/null; then
        OS_NAME=$(uname -s)
        OS_VERSION=$(uname -r)
    else
        OS_NAME="Unknown"
        OS_VERSION="Unknown"
    fi

    echo "[信息] 检测到操作系统: $OS_NAME $OS_VERSION"
}

# 检查root权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "[提示] 建议使用sudo权限运行以安装系统依赖"
        echo ""
    fi
}

# 安装Python 3
install_python() {
    echo "[步骤1] 检查Python 3..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "[完成] $PYTHON_VERSION 已安装"
    else
        echo "[安装] 正在安装Python 3..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip
        else
            echo "[错误] 无法自动安装Python，请手动安装"
            exit 1
        fi
    fi
}

# 安装Tkinter（关键依赖）
install_tkinter() {
    echo "[步骤2] 检查Tkinter..."

    if python3 -c "import tkinter" 2>/dev/null; then
        echo "[完成] Tkinter已安装"
    else
        echo "[安装] 正在安装Tkinter..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-tk python3-pil python3-pil.imagetk
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-tkinter
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-tkinter
        else
            echo "[警告] 无法自动安装Tkinter"
            echo "请手动执行以下命令之一:"
            echo "  Ubuntu/Debian: sudo apt-get install python3-tk python3-pil python3-pil.imagetk"
            echo "  CentOS/RHEL: sudo yum install python3-tkinter"
            echo "  Fedora: sudo dnf install python3-tkinter"
        fi
    fi
}

# 安装Playwright浏览器
install_playwright() {
    echo "[步骤3] 检查Playwright..."

    pip3 install playwright 2>/dev/null || sudo -H pip3 install playwright

    echo "[安装] 正在安装浏览器引擎..."
    playwright install chromium 2>/dev/null || playwright install firefox 2>/dev/null || true

    echo "[完成] Playwright浏览器安装完成"
}

# 安装应用依赖
install_app_dependencies() {
    echo "[步骤4] 安装应用Python依赖..."

    cd "$(dirname "$0")"
    pip3 install -r requirements.txt

    echo "[完成] 应用依赖安装完成"
}

# 验证安装
verify_installation() {
    echo "[验证] 检查安装结果..."

    local errors=0

    if python3 -c "import tkinter" 2>/dev/null; then
        echo "[OK] Tkinter"
    else
        echo "[失败] Tkinter"
        errors=$((errors + 1))
    fi

    if python3 -c "import PIL" 2>/dev/null; then
        echo "[OK] Pillow"
    else
        echo "[失败] Pillow"
        errors=$((errors + 1))
    fi

    if python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
        echo "[OK] Playwright"
    else
        echo "[失败] Playwright"
        errors=$((errors + 1))
    fi

    if python3 -c "import docx" 2>/dev/null; then
        echo "[OK] python-docx"
    else
        echo "[失败] python-docx"
        errors=$((errors + 1))
    fi

    if python3 -c "import keyring" 2>/dev/null; then
        echo "[OK] keyring"
    else
        echo "[失败] keyring"
        errors=$((errors + 1))
    fi

    return $errors
}

# 主函数
main() {
    detect_os
    check_root

    echo ""
    read -p "是否开始安装依赖? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "已取消安装"
        exit 0
    fi

    echo ""
    install_python
    install_tkinter
    install_playwright
    install_app_dependencies

    echo ""
    if verify_installation; then
        echo ""
        echo "========================================"
        echo "  安装完成！"
        echo "========================================"
        echo ""
        echo "运行命令: ./start_linux.sh"
    else
        echo ""
        echo "========================================"
        echo "  部分依赖安装失败"
        echo "========================================"
        echo ""
        echo "请查看上述失败信息，手动安装缺失的依赖"
        exit 1
    fi
}

main "$@"