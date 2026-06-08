# -*- coding: utf-8 -*-
"""
供应商不良行为查询工具 - 程序入口

支持平台: Windows 10/11, 统信UOS, 银河麒麟, 中标麒麟
"""

import sys
import logging
import tkinter as tk
from tkinter import messagebox
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME
from gui.login_window import LoginWindow, show_login_window
from gui.main_window import MainWindow
from utils.logger import logger, setup_logger


def parse_args():
    """解析命令行参数"""
    args = {
        "debug": False,
        "test": False
    }
    
    for arg in sys.argv[1:]:
        if arg in ("--debug", "-d"):
            args["debug"] = True
        elif arg in ("--test", "-t"):
            args["test"] = True
    
    return args


def check_tkinter_dependency():
    """检查Tkinter是否可用"""
    try:
        test = tk.Tk()
        test.destroy()
        return True
    except Exception as e:
        return False, str(e)


def check_system_dependencies():
    """检查系统依赖"""
    issues = []

    # 检查Tkinter
    tk_ok, tk_error = check_tkinter_dependency()
    if not tk_ok:
        issues.append(f"Tkinter: {tk_error}")

    return issues


def show_dependency_error(issues: list):
    """显示依赖错误对话框"""
    error_msg = "缺少必要的系统依赖：\n\n"
    for issue in issues:
        error_msg += f"• {issue}\n\n"

    error_msg += "请安装缺失的依赖后重试。\n\n"

    if sys.platform == "win32":
        error_msg += "Windows系统安装命令：\npip install tkintertable pillow\n"
    else:
        error_msg += "国产系统安装命令：\nsudo apt-get install python3-tk python3-pil python3-pil.imagetk\n"
        error_msg += "或执行项目中的 install_deps.sh 脚本"

    messagebox.showerror("依赖检查失败", error_msg)


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 设置日志级别
    if args["debug"]:
        logger.setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
        logger.debug(f"命令行参数: {sys.argv}")
    
    logger.info("=" * 60)
    logger.info(f"{APP_NAME} 启动")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"操作系统: {sys.platform}")
    logger.info("=" * 60)

    # 检查系统依赖
    issues = check_system_dependencies()
    if issues:
        logger.error(f"系统依赖检查失败: {issues}")
        show_dependency_error(issues)
        sys.exit(1)

    try:
        # 创建登录窗口
        def on_login_success():
            logger.info("登录成功，显示主界面")
            main_window = MainWindow()
            main_window.show()

        # 显示登录窗口
        login_window = LoginWindow(on_login_success=on_login_success)
        login_window.show()

    except KeyboardInterrupt:
        logger.info("用户中断程序")
        sys.exit(0)

    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("错误", f"程序发生异常：\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()