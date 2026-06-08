# -*- coding: utf-8 -*-
"""
查询引擎模块 - 核心查询逻辑
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from config import GENERAL_SITES, ENGINEERING_SITES
from core.browser import BrowserController, get_browser, close_browser
from core.screenshot import screenshot_manager
from utils.file_utils import file_utils
from utils.logger import logger


class QueryStatus(Enum):
    """查询状态"""
    PENDING = "待查询"
    IN_PROGRESS = "查询中"
    SUCCESS = "成功"
    FAILED = "失败"
    SKIPPED = "跳过"


@dataclass
class SiteResult:
    """站点查询结果"""
    site_name: str
    site_url: str
    status: QueryStatus
    screenshot_path: Optional[Path] = None
    error_message: Optional[str] = None


class QueryEngine:
    """查询引擎"""

    def __init__(
        self,
        supplier_name: str,
        credit_code: str,
        is_engineering: bool,
        output_dir: Path,
        progress_callback: Optional[Callable] = None,
        log_callback: Optional[Callable] = None
    ):
        """
        初始化查询引擎

        Args:
            supplier_name: 供应商名称
            credit_code: 统一社会信用代码
            is_engineering: 是否工程类
            output_dir: 输出目录
            progress_callback: 进度回调函数 (current, total, message)
            log_callback: 日志回调函数 (message)
        """
        self.supplier_name = supplier_name
        self.credit_code = credit_code
        self.is_engineering = is_engineering
        self.output_dir = output_dir
        self.progress_callback = progress_callback
        self.log_callback = log_callback

        self._browser: Optional[BrowserController] = None
        self._results: List[SiteResult] = []
        self._is_cancelled = False

        # 确定要查询的站点列表
        self._sites = self._build_site_list()

    def _build_site_list(self) -> List[Dict]:
        """构建查询站点列表"""
        sites = []

        # 添加通用站点
        for site in GENERAL_SITES:
            sites.append({
                "name": site["name"],
                "url": site["url"],
                "xpath": site.get("xpath", ""),
                "type": "general"
            })

        # 如果是工程类，添加专属站点
        if self.is_engineering:
            for site in ENGINEERING_SITES:
                sites.append({
                    "name": site["name"],
                    "url": site["url"],
                    "xpath": site.get("xpath", ""),
                    "type": "engineering"
                })

        self._log(f"共需查询 {len(sites)} 个站点")
        return sites

    def _log(self, message: str):
        """输出日志"""
        logger.info(message)
        if self.log_callback:
            self.log_callback(message)

    def _update_progress(self, current: int, total: int, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(current, total, message)

    def _show_captcha_dialog(self, site_name: str) -> bool:
        """
        显示验证码提示对话框

        Args:
            site_name: 网站名称

        Returns:
            用户是否已完成验证
        """
        # 创建模式对话框
        dialog = tk.Toplevel()
        dialog.title("验证码输入")
        dialog.geometry("400x150")
        dialog.resizable(False, False)

        # 让对话框居中
        dialog.transient()

        # 消息标签
        msg = tk.Label(
            dialog,
            text=f"请在浏览器中完成 {site_name} 的验证码验证",
            font=("Microsoft YaHei", 12)
        )
        msg.pack(pady=20)

        # 完成按钮
        def on_complete():
            dialog.destroy()
            dialog.result = True

        btn = tk.Button(dialog, text="已完成验证", command=on_complete, width=15)
        btn.pack(pady=10)

        dialog.result = False
        dialog.grab_set()

        # 等待用户点击
        dialog.wait_window()

        return dialog.result

    def query_single_site(self, site: Dict) -> SiteResult:
        """
        查询单个站点

        Args:
            site: 站点信息字典

        Returns:
            查询结果
        """
        site_name = site["name"]
        site_url = site["url"]

        self._log(f"正在查询: {site_name}")
        self._log(f"URL: {site_url}")

        try:
            # 导航到站点
            if not self._browser.navigate_to(site_url):
                return SiteResult(
                    site_name=site_name,
                    site_url=site_url,
                    status=QueryStatus.FAILED,
                    error_message="页面加载失败"
                )

            # 随机延时
            file_utils.random_delay()

            # 等待页面稳定
            self._browser.wait_for_selector("body", timeout=5000)

            # 检查是否有验证码（需要人工处理）
            # 这里简化处理，实际可能需要检测验证码元素
            # if self._detect_captcha():
            #     self._log(f"检测到验证码，暂停等待人工验证...")
            #     if not self._show_captcha_dialog(site_name):
            #         return SiteResult(
            #             site_name=site_name,
            #             site_url=site_url,
            #             status=QueryStatus.FAILED,
            #             error_message="用户取消验证码验证"
            #         )

            # 截取页面
            screenshot_path = screenshot_manager.capture_and_save(
                self._browser._page,
                self.output_dir,
                site_name,
                self.supplier_name
            )

            if screenshot_path:
                return SiteResult(
                    site_name=site_name,
                    site_url=site_url,
                    status=QueryStatus.SUCCESS,
                    screenshot_path=screenshot_path
                )
            else:
                return SiteResult(
                    site_name=site_name,
                    site_url=site_url,
                    status=QueryStatus.FAILED,
                    error_message="截图失败"
                )

        except Exception as e:
            logger.error(f"查询站点异常: {site_name}, 错误: {e}")
            return SiteResult(
                site_name=site_name,
                site_url=site_url,
                status=QueryStatus.FAILED,
                error_message=str(e)
            )

    def execute(self) -> List[SiteResult]:
        """
        执行批量查询

        Returns:
            所有站点的查询结果
        """
        total = len(self._sites)
        self._log(f"开始查询，共 {total} 个站点")
        self._log(f"供应商: {self.supplier_name}")
        self._log(f"统一社会信用代码: {self.credit_code}")
        self._log(f"工程类供应商: {'是' if self.is_engineering else '否'}")

        # 初始化浏览器
        self._browser = get_browser()
        if not self._browser.initialize():
            self._log("浏览器初始化失败")
            return []

        try:
            for index, site in enumerate(self._sites, 1):
                if self._is_cancelled:
                    self._log("查询已取消")
                    break

                # 更新进度
                self._update_progress(index - 1, total, f"准备查询: {site['name']}")

                # 查询单个站点
                result = self.query_single_site(site)
                self._results.append(result)

                # 记录结果
                if result.status == QueryStatus.SUCCESS:
                    self._log(f"✓ {site['name']} - 成功")
                else:
                    self._log(f"✗ {site['name']} - 失败: {result.error_message}")

                # 站点间延时
                if index < total:
                    file_utils.random_delay()

            # 完成
            success_count = sum(1 for r in self._results if r.status == QueryStatus.SUCCESS)
            failed_count = sum(1 for r in self._results if r.status == QueryStatus.FAILED)

            self._update_progress(total, total, "查询完成")
            self._log(f"查询完成: 成功 {success_count}, 失败 {failed_count}")

        except Exception as e:
            self._log(f"查询过程异常: {e}")
            logger.error(f"查询引擎异常: {e}")

        finally:
            # 关闭浏览器
            close_browser()

        return self._results

    def cancel(self):
        """取消查询"""
        self._is_cancelled = True
        self._log("正在取消查询...")

    @property
    def results(self) -> List[SiteResult]:
        """获取查询结果"""
        return self._results


# 辅助函数：创建查询引擎
def create_query_engine(
    supplier_name: str,
    credit_code: str,
    is_engineering: bool,
    output_dir: Path,
    progress_callback: Optional[Callable] = None,
    log_callback: Optional[Callable] = None
) -> QueryEngine:
    """创建查询引擎实例"""
    return QueryEngine(
        supplier_name=supplier_name,
        credit_code=credit_code,
        is_engineering=is_engineering,
        output_dir=output_dir,
        progress_callback=progress_callback,
        log_callback=log_callback
    )