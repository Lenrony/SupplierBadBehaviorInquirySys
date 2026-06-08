# -*- coding: utf-8 -*-
"""
登录窗口模块 - 用户登录界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from typing import Optional, Callable

from core.auth import auth_manager
from utils.logger import logger
from config import APP_NAME, APP_VERSION


class LoginWindow:
    """登录窗口类"""

    def __init__(self, on_login_success: Optional[Callable] = None):
        """
        初始化登录窗口

        Args:
            on_login_success: 登录成功后的回调函数
        """
        self.on_login_success = on_login_success
        self._window: Optional[tk.Tk] = None
        self._username_var: Optional[tk.StringVar] = None
        self._password_var: Optional[tk.StringVar] = None
        self._remember_var: Optional[tk.BooleanVar] = None
        self._is_logged_in = False

    def create_window(self) -> tk.Tk:
        """创建登录窗口"""
        # 创建主窗口
        self._window = tk.Tk()
        self._window.title(f"{APP_NAME} v{APP_VERSION}")
        self._window.geometry("400x320")
        self._window.resizable(False, False)

        # 居中显示
        self._center_window()

        # 设置样式
        self._setup_styles()

        # 创建控件
        self._create_widgets()

        # 加载保存的凭证
        self._load_saved_credentials()

        # 绑定事件
        self._window.protocol("WM_DELETE_WINDOW", self._on_close)

        return self._window

    def _center_window(self):
        """窗口居中显示"""
        self._window.update_idletasks()
        width = self._window.winfo_width()
        height = self._window.winfo_height()
        x = (self._window.winfo_screenwidth() // 2) - (width // 2)
        y = (self._window.winfo_screenheight() // 2) - (height // 2)
        self._window.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_styles(self):
        """设置窗口样式"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

    def _create_widgets(self):
        """创建窗口控件"""
        # 主容器
        main_frame = ttk.Frame(self._window, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(
            main_frame,
            text=APP_NAME,
            font=("Microsoft YaHei", 18, "bold"),
            fg="#333333"
        )
        title_label.pack(pady=(0, 5))

        # 副标题
        subtitle_label = tk.Label(
            main_frame,
            text="供应商不良行为自动查询与归档工具",
            font=("Microsoft YaHei", 10),
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 20))

        # 用户名
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="用户名:", width=10).pack(side=tk.LEFT)
        self._username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self._username_var, width=25)
        username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        username_entry.bind("<Return>", lambda e: self._password_entry.focus())

        # 密码
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        ttk.Label(password_frame, text="密码:", width=10).pack(side=tk.LEFT)
        self._password_var = tk.StringVar()
        self._password_entry = ttk.Entry(
            password_frame,
            textvariable=self._password_var,
            show="*",
            width=25
        )
        self._password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._password_entry.bind("<Return>", lambda e: self._on_login())

        # 记住密码
        remember_frame = ttk.Frame(main_frame)
        remember_frame.pack(fill=tk.X, pady=10)
        self._remember_var = tk.BooleanVar(value=False)
        remember_check = ttk.Checkbutton(
            remember_frame,
            text="记住密码",
            variable=self._remember_var
        )
        remember_check.pack(side=tk.LEFT)

        # 登录按钮
        login_btn = ttk.Button(
            main_frame,
            text="登录",
            command=self._on_login,
            width=20
        )
        login_btn.pack(pady=(10, 5))

        # 退出按钮
        exit_btn = ttk.Button(
            main_frame,
            text="退出",
            command=self._on_close,
            width=20
        )
        exit_btn.pack(pady=5)

        # 状态栏
        self._status_label = tk.Label(
            main_frame,
            text="请输入账号密码登录",
            font=("Microsoft YaHei", 9),
            fg="#888888"
        )
        self._status_label.pack(side=tk.BOTTOM, pady=(10, 0))

        # 设置焦点
        username_entry.focus()

    def _load_saved_credentials(self):
        """加载保存的凭证"""
        try:
            username, password = auth_manager.load_saved_credentials()
            if username and password:
                self._username_var.set(username)
                self._password_var.set(password)
                self._remember_var.set(True)
                logger.info("已加载保存的登录凭证")
        except Exception as e:
            logger.warning(f"加载凭证失败: {e}")

    def _on_login(self):
        """处理登录按钮点击"""
        username = self._username_var.get().strip()
        password = self._password_var.get().strip()

        if not username:
            self._status_label.config(text="请输入用户名", fg="#cc0000")
            return

        if not password:
            self._status_label.config(text="请输入密码", fg="#cc0000")
            return

        # 更新状态
        self._status_label.config(text="正在验证...", fg="#0066cc")

        # 验证登录
        if auth_manager.login(username, password):
            self._status_label.config(text="登录成功", fg="#00aa00")

            # 保存凭证
            if self._remember_var.get():
                auth_manager.save_credentials(username, password)
            else:
                auth_manager.clear_credentials()

            logger.info(f"用户 {username} 登录成功")

            # 延迟关闭，等待用户看到成功提示
            self._window.after(500, self._close_and_callback)

        else:
            self._status_label.config(text="用户名或密码错误", fg="#cc0000")
            logger.warning(f"用户 {username} 登录失败")

    def _close_and_callback(self):
        """关闭窗口并调用回调"""
        self._is_logged_in = True
        self._window.destroy()
        if self.on_login_success:
            self.on_login_success()

    def _on_close(self):
        """处理窗口关闭"""
        logger.info("用户关闭登录窗口")
        self._window.destroy()
        sys.exit(0)

    def show(self):
        """显示登录窗口"""
        if not self._window:
            self.create_window()
        self._window.mainloop()

    @property
    def is_logged_in(self) -> bool:
        """是否已登录"""
        return self._is_logged_in


def show_login_window(on_login_success: Optional[Callable] = None) -> LoginWindow:
    """
    显示登录窗口的便捷函数

    Args:
        on_login_success: 登录成功后的回调函数

    Returns:
        LoginWindow实例
    """
    login_window = LoginWindow(on_login_success=on_login_success)
    login_window.create_window()
    return login_window