# -*- coding: utf-8 -*-
"""
主操作窗口模块 - 查询操作界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
from pathlib import Path
from typing import Optional

from core.query_engine import create_query_engine, QueryStatus, SiteResult
from core.report_generator import create_report_generator
from utils.file_utils import file_utils
from utils.logger import logger
from config import APP_NAME, APP_VERSION, get_default_download_dir, GENERAL_SITES, ENGINEERING_SITES


class MainWindow:
    """主操作窗口类"""

    def __init__(self):
        self._window: Optional[tk.Tk] = None
        self._supplier_name_var: Optional[tk.StringVar] = None
        self._credit_code_var: Optional[tk.StringVar] = None
        self._is_engineering_var: Optional[tk.BooleanVar] = None
        self._output_dir_var: Optional[tk.StringVar] = None
        self._progress_var: Optional[tk.StringVar] = None
        self._log_text: Optional[scrolledtext.ScrolledText] = None

        self._query_engine: Optional[any] = None
        self._is_querying = False
        self._output_dir: Optional[Path] = None

    def create_window(self) -> tk.Tk:
        """创建主窗口"""
        # 创建主窗口
        self._window = tk.Tk()
        self._window.title(f"{APP_NAME} - 主界面")
        self._window.geometry("900x700")
        self._window.minsize(800, 600)

        # 居中显示
        self._center_window()

        # 创建控件
        self._create_widgets()

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

    def _create_widgets(self):
        """创建窗口控件"""
        # 创建菜单栏
        self._create_menu()

        # 创建主容器
        main_frame = ttk.Frame(self._window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === 左侧输入区域 ===
        left_frame = ttk.LabelFrame(main_frame, text="查询条件", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        left_frame.configure(width=350)

        self._create_input_form(left_frame)

        # === 右侧日志区域 ===
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._create_log_area(right_frame)
        self._create_progress_area(right_frame)

    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self._window)
        self._window.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开输出目录", command=self._open_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用手册", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)

    def _create_input_form(self, parent):
        """创建输入表单"""
        # 供应商名称
        ttk.Label(parent, text="供应商名称:").pack(anchor=tk.W, pady=(10, 0))
        self._supplier_name_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self._supplier_name_var, width=35).pack(
            anchor=tk.W, fill=tk.X, pady=(5, 10)
        )

        # 统一社会信用代码
        ttk.Label(parent, text="统一社会信用代码:").pack(anchor=tk.W)
        self._credit_code_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self._credit_code_var, width=35).pack(
            anchor=tk.W, fill=tk.X, pady=5
        )

        # 是否工程类
        ttk.Label(parent, text="是否工程类供应商:").pack(anchor=tk.W, pady=(10, 0))
        self._is_engineering_var = tk.BooleanVar(value=False)
        engineering_frame = ttk.Frame(parent)
        engineering_frame.pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(
            engineering_frame,
            text="是",
            variable=self._is_engineering_var,
            value=True
        ).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(
            engineering_frame,
            text="否",
            variable=self._is_engineering_var,
            value=False
        ).pack(side=tk.LEFT)

        # 查询站点说明
        sites_frame = ttk.LabelFrame(parent, text="将查询的站点", padding="5")
        sites_frame.pack(fill=tk.X, pady=10)

        self._sites_text = tk.Text(sites_frame, height=8, width=40, state=tk.DISABLED)
        self._sites_text.pack()
        self._update_sites_text()

        # 绑定工程类选择变化
        self._is_engineering_var.trace_add("write", lambda *args: self._update_sites_text())

        # 文件存储目录
        ttk.Label(parent, text="文件存储目录:").pack(anchor=tk.W, pady=(10, 0))
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(anchor=tk.W, fill=tk.X, pady=5)
        self._output_dir_var = tk.StringVar(value=str(get_default_download_dir()))
        ttk.Entry(dir_frame, textvariable=self._output_dir_var, width=30).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(
            dir_frame,
            text="浏览",
            command=self._browse_output_dir,
            width=6
        ).pack(side=tk.LEFT, padx=(5, 0))

        # 按钮区域
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=20)

        self._start_btn = ttk.Button(
            btn_frame,
            text="开始查询",
            command=self._start_query,
            width=15
        )
        self._start_btn.pack(side=tk.LEFT, padx=5)

        self._cancel_btn = ttk.Button(
            btn_frame,
            text="取消",
            command=self._cancel_query,
            width=15,
            state=tk.DISABLED
        )
        self._cancel_btn.pack(side=tk.LEFT, padx=5)

    def _update_sites_text(self):
        """更新站点列表显示"""
        is_engineering = self._is_engineering_var.get()

        text = "【通用站点】\n"
        for site in GENERAL_SITES:
            text += f"• {site['name']}\n"

        if is_engineering:
            text += "\n【工程类专属站点】\n"
            for site in ENGINEERING_SITES:
                text += f"• {site['name']}\n"

        self._sites_text.config(state=tk.NORMAL)
        self._sites_text.delete("1.0", tk.END)
        self._sites_text.insert("1.0", text)
        self._sites_text.config(state=tk.DISABLED)

    def _create_log_area(self, parent):
        """创建日志区域"""
        log_label = ttk.Label(parent, text="运行日志:")
        log_label.pack(anchor=tk.W)

        self._log_text = scrolledtext.ScrolledText(
            parent,
            height=20,
            width=50,
            state=tk.DISABLED,
            font=("Consolas", 9)
        )
        self._log_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 配置标签颜色
        self._log_text.tag_configure("info", foreground="#000000")
        self._log_text.tag_configure("success", foreground="#00aa00")
        self._log_text.tag_configure("warning", foreground="#cc6600")
        self._log_text.tag_configure("error", foreground="#cc0000")

    def _create_progress_area(self, parent):
        """创建进度区域"""
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=5)

        self._progress_var = tk.StringVar(value="就绪")
        self._progress_label = tk.Label(
            progress_frame,
            textvariable=self._progress_var,
            font=("Microsoft YaHei", 9)
        )
        self._progress_label.pack(side=tk.LEFT)

        self._progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=200
        )
        self._progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

    def _browse_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(
            title="选择文件存储目录",
            initialdir=self._output_dir_var.get()
        )
        if directory:
            self._output_dir_var.set(directory)

    def _start_query(self):
        """开始查询"""
        # 验证输入
        supplier_name = self._supplier_name_var.get().strip()
        credit_code = self._credit_code_var.get().strip()
        is_engineering = self._is_engineering_var.get()
        output_dir_path = Path(self._output_dir_var.get().strip())

        if not supplier_name:
            messagebox.showwarning("输入验证", "请输入供应商名称")
            return

        if not credit_code:
            messagebox.showwarning("输入验证", "请输入统一社会信用代码")
            return

        if not output_dir_path.exists():
            # 尝试创建目录
            success, error = file_utils.ensure_directory_writable(output_dir_path)
            if not success:
                messagebox.showerror("目录错误", f"无法创建输出目录:\n{error}")
                return

        # 检查目录写入权限
        if not file_utils.check_write_permission(output_dir_path):
            messagebox.showerror("权限错误", f"无写入权限:\n{output_dir_path}")
            return

        # 创建输出文件夹
        try:
            self._output_dir = file_utils.create_output_folder(supplier_name)
        except Exception as e:
            messagebox.showerror("创建文件夹失败", str(e))
            return

        # 记录查询信息
        self._log_message(f"=" * 50, "info")
        self._log_message(f"开始查询", "info")
        self._log_message(f"供应商: {supplier_name}", "info")
        self._log_message(f"信用代码: {credit_code}", "info")
        self._log_message(f"工程类: {'是' if is_engineering else '否'}", "info")
        self._log_message(f"输出目录: {self._output_dir}", "info")
        self._log_message(f"=" * 50, "info")

        # 禁用开始按钮
        self._start_btn.config(state=tk.DISABLED)
        self._cancel_btn.config(state=tk.NORMAL)
        self._is_querying = True

        # 在后台线程执行查询
        thread = threading.Thread(target=self._run_query, daemon=True)
        thread.start()

    def _run_query(self):
        """在后台线程运行查询"""
        try:
            supplier_name = self._supplier_name_var.get().strip()
            credit_code = self._credit_code_var.get().strip()
            is_engineering = self._is_engineering_var.get()

            # 创建查询引擎
            self._query_engine = create_query_engine(
                supplier_name=supplier_name,
                credit_code=credit_code,
                is_engineering=is_engineering,
                output_dir=self._output_dir,
                progress_callback=self._update_progress,
                log_callback=self._log_message
            )

            # 执行查询
            results = self._query_engine.execute()

            # 生成报告
            self._log_message("-" * 30, "info")
            self._log_message("正在生成报告...", "info")

            try:
                report_gen = create_report_generator(self._output_dir)
                report_path = report_gen.generate(
                    supplier_name=supplier_name,
                    credit_code=credit_code,
                    is_engineering=is_engineering,
                    results=results
                )
                self._log_message(f"报告已生成: {report_path.name}", "success")

                # 打开输出目录
                self._open_output_dir()

            except Exception as e:
                self._log_message(f"报告生成失败: {e}", "error")
                logger.error(f"报告生成失败: {e}")

            # 查询完成
            self._log_message("=" * 50, "success")
            self._log_message("查询任务完成", "success")
            self._log_message("=" * 50, "success")

        except Exception as e:
            self._log_message(f"查询过程异常: {e}", "error")
            logger.error(f"查询异常: {e}")

        finally:
            # 恢复按钮状态
            self._window.after(0, self._query_finished)

    def _query_finished(self):
        """查询完成后的处理"""
        self._start_btn.config(state=tk.NORMAL)
        self._cancel_btn.config(state=tk.DISABLED)
        self._is_querying = False
        self._progress_var.set("完成")
        self._progress_bar["value"] = 100

    def _cancel_query(self):
        """取消查询"""
        if self._query_engine:
            self._query_engine.cancel()
            self._log_message("已发送取消请求...", "warning")

    def _update_progress(self, current: int, total: int, message: str):
        """更新进度回调"""
        def _update():
            percentage = int((current / total) * 100) if total > 0 else 0
            self._progress_var.set(f"{message} ({current}/{total})")
            self._progress_bar["value"] = percentage

        self._window.after(0, _update)

    def _log_message(self, message: str, level: str = "info"):
        """输出日志消息"""
        def _append():
            if self._log_text:
                self._log_text.config(state=tk.NORMAL)
                self._log_text.insert(tk.END, message + "\n", level)
                self._log_text.see(tk.END)
                self._log_text.config(state=tk.DISABLED)

        self._window.after(0, _append)

    def _open_output_dir(self):
        """打开输出目录"""
        if self._output_dir and self._output_dir.exists():
            try:
                import platform
                system = platform.system()
                if system == "Windows":
                    import os
                    os.startfile(self._output_dir)
                elif system == "Linux":
                    import subprocess
                    subprocess.run(["xdg-open", str(self._output_dir)])
            except Exception as e:
                logger.error(f"打开目录失败: {e}")
                messagebox.showwarning("提示", f"无法自动打开目录:\n{self._output_dir}")

    def _show_help(self):
        """显示帮助"""
        help_text = """
        使用手册

        1. 输入供应商名称和统一社会信用代码
        2. 选择是否工程类供应商
        3. 选择文件存储目录
        4. 点击"开始查询"按钮
        5. 等待查询完成，查看生成的报告

        注意事项：
        - 查询过程请勿关闭程序
        - 截图和报告将保存在同一文件夹
        - 如遇验证码，请按提示在浏览器中完成验证
        """
        messagebox.showinfo("使用手册", help_text)

    def _show_about(self):
        """显示关于"""
        about_text = f"""
        {APP_NAME}

        版本: {APP_VERSION}

        供应商不良行为自动查询与归档工具

        支持的查询站点：
        - 通用站点：5个
        - 工程类站点：2个（仅工程类供应商）
        """
        messagebox.showinfo("关于", about_text)

    def _on_close(self):
        """关闭窗口"""
        if self._is_querying:
            if messagebox.askyesno("确认退出", "查询正在进行中，确定要退出吗？"):
                if self._query_engine:
                    self._query_engine.cancel()
                self._window.destroy()
                sys.exit(0)
        else:
            self._window.destroy()
            sys.exit(0)

    def show(self):
        """显示主窗口"""
        if not self._window:
            self.create_window()
        self._window.mainloop()