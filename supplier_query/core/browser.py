# -*- coding: utf-8 -*-
"""
浏览器控制模块 - Playwright浏览器自动化封装
"""

import asyncio
import sys
from typing import Optional, Callable
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from playwright._impl._api_types import TimeoutError
from config import get_browser_config, PAGE_LOAD_TIMEOUT, MAX_RETRIES
from utils.logger import logger


class BrowserController:
    """浏览器控制器"""

    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._is_initialized = False

    def initialize(self) -> bool:
        """
        初始化浏览器

        Returns:
            初始化是否成功
        """
        try:
            if self._is_initialized:
                return True

            logger.info("正在初始化浏览器...")
            self._playwright = sync_playwright().start()

            config = get_browser_config()
            browser_type = config["browser_type"]

            # 启动浏览器
            if browser_type == "chromium":
                self._browser = self._playwright.chromium.launch(
                    channel=config.get("channel"),
                    headless=config.get("headless", False),
                )
            elif browser_type == "firefox":
                self._browser = self._playwright.firefox.launch(
                    headless=config.get("headless", False),
                )
            else:
                self._browser = self._playwright.chromium.launch(
                    headless=False,
                )

            # 创建上下文
            self._context = self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # 创建页面
            self._page = self._context.new_page()
            self._page.set_default_timeout(PAGE_LOAD_TIMEOUT)

            self._is_initialized = True
            logger.info("浏览器初始化成功")
            return True

        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            return False

    def navigate_to(self, url: str, retry_count: int = 0) -> bool:
        """
        导航到指定URL

        Args:
            url: 目标URL
            retry_count: 当前重试次数

        Returns:
            是否成功
        """
        if not self._is_initialized:
            if not self.initialize():
                return False

        try:
            logger.info(f"正在访问: {url}")
            self._page.goto(url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT)
            logger.info(f"页面加载完成: {url}")
            return True

        except TimeoutError:
            logger.warning(f"页面加载超时: {url}")
            if retry_count < MAX_RETRIES:
                logger.info(f"第{retry_count + 1}次重试...")
                return self.navigate_to(url, retry_count + 1)
            return False

        except Exception as e:
            logger.error(f"导航失败: {url}, 错误: {e}")
            if retry_count < MAX_RETRIES:
                return self.navigate_to(url, retry_count + 1)
            return False

    def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """
        等待元素出现

        Args:
            selector: CSS选择器或XPath
            timeout: 超时时间（毫秒）

        Returns:
            元素是否出现
        """
        try:
            self._page.wait_for_selector(selector, timeout=timeout, state="attached")
            return True
        except Exception as e:
            logger.warning(f"等待元素超时: {selector}")
            return False

    def fill_input(self, selector: str, value: str) -> bool:
        """
        填写输入框

        Args:
            selector: 选择器
            value: 输入值

        Returns:
            是否成功
        """
        try:
            self._page.fill(selector, value)
            logger.debug(f"已填写: {selector} = {value}")
            return True
        except Exception as e:
            logger.error(f"填写失败: {selector}, 错误: {e}")
            return False

    def click(self, selector: str) -> bool:
        """
        点击元素

        Args:
            selector: 选择器

        Returns:
            是否成功
        """
        try:
            self._page.click(selector)
            logger.debug(f"已点击: {selector}")
            return True
        except Exception as e:
            logger.error(f"点击失败: {selector}, 错误: {e}")
            return False

    def screenshot_full_page(self, save_path: str) -> bool:
        """
        截取整页截图

        Args:
            save_path: 保存路径

        Returns:
            是否成功
        """
        try:
            # 等待页面完全加载
            self._page.wait_for_load_state("networkidle")

            # 执行截图
            self._page.screenshot(
                path=save_path,
                full_page=True,
                timeout=30000
            )
            logger.info(f"截图已保存: {save_path}")
            return True

        except Exception as e:
            logger.error(f"截图失败: {e}")
            return False

    def get_page_title(self) -> str:
        """获取页面标题"""
        if self._page:
            return self._page.title()
        return ""

    def execute_script(self, script: str):
        """执行JavaScript"""
        try:
            return self._page.evaluate(script)
        except Exception as e:
            logger.error(f"执行脚本失败: {e}")
            return None

    def close(self):
        """关闭浏览器"""
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()

            self._is_initialized = False
            logger.info("浏览器已关闭")

        except Exception as e:
            logger.error(f"关闭浏览器时出错: {e}")

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


# 全局浏览器实例（延迟初始化）
_browser_instance: Optional[BrowserController] = None


def get_browser() -> BrowserController:
    """获取浏览器实例"""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = BrowserController()
    return _browser_instance


def close_browser():
    """关闭浏览器实例"""
    global _browser_instance
    if _browser_instance:
        _browser_instance.close()
        _browser_instance = None