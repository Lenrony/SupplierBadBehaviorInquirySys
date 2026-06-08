# -*- coding: utf-8 -*-
"""
文件操作工具模块 - 跨平台文件处理
"""

import os
import shutil
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from config import get_default_download_dir, DELAY_MIN, DELAY_MAX
from utils.logger import logger


class FileUtils:
    """文件操作工具类"""

    @staticmethod
    def create_output_folder(supplier_name: str) -> Path:
        """
        创建输出文件夹

        Args:
            supplier_name: 供应商名称

        Returns:
            创建的文件夹路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        # 清理供应商名称中的非法字符
        safe_name = FileUtils.sanitize_filename(supplier_name)
        folder_name = f"{safe_name}_{timestamp}"

        output_dir = get_default_download_dir() / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建输出文件夹: {output_dir}")
        return output_dir

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        清理文件名中的非法字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的安全文件名
        """
        # Windows/Unix通用：替换非法字符
        illegal_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '\0']
        safe_name = filename
        for char in illegal_chars:
            safe_name = safe_name.replace(char, '_')

        # 限制长度
        if len(safe_name) > 100:
            safe_name = safe_name[:100]

        return safe_name.strip()

    @staticmethod
    def generate_screenshot_name(site_name: str, supplier_name: str) -> str:
        """
        生成截图文件名

        Args:
            site_name: 网站名称
            supplier_name: 供应商名称

        Returns:
            截图文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_site = FileUtils.sanitize_filename(site_name)
        safe_supplier = FileUtils.sanitize_filename(supplier_name)
        return f"{safe_site}_{safe_supplier}_{timestamp}.png"

    @staticmethod
    def generate_report_name(supplier_name: str) -> str:
        """
        生成报告文件名

        Args:
            supplier_name: 供应商名称

        Returns:
            报告文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        safe_name = FileUtils.sanitize_filename(supplier_name)
        return f"供应商不良行为查询报告_{safe_name}_{timestamp}.docx"

    @staticmethod
    def random_delay():
        """随机延时（防爬虫）"""
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        logger.debug(f"延时等待: {delay:.2f}秒")
        time.sleep(delay)

    @staticmethod
    def check_write_permission(directory: Path) -> bool:
        """
        检查目录是否可写

        Args:
            directory: 待检查的目录

        Returns:
            是否可写
        """
        try:
            # 尝试创建临时文件测试
            test_file = directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except Exception as e:
            logger.warning(f"目录不可写: {directory}, 错误: {e}")
            return False

    @staticmethod
    def ensure_directory_writable(directory: Path) -> tuple:
        """
        确保目录可写，必要时创建或修改权限

        Args:
            directory: 目标目录

        Returns:
            (成功标志, 错误信息)
        """
        try:
            # 确保父目录存在
            directory.mkdir(parents=True, exist_ok=True)

            # 检查权限
            if not FileUtils.check_write_permission(directory):
                # 尝试修改权限
                os.chmod(directory, 0o755)
                if not FileUtils.check_write_permission(directory):
                    return False, f"目录无写入权限: {directory}"

            return True, ""
        except PermissionError as e:
            return False, f"权限不足，无法创建目录: {directory}"
        except Exception as e:
            return False, f"创建目录失败: {e}"

    @staticmethod
    def list_screenshots(folder: Path) -> List[Path]:
        """
        列出文件夹中的所有截图

        Args:
            folder: 文件夹路径

        Returns:
            截图文件列表
        """
        if not folder.exists():
            return []

        screenshots = list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
        return sorted(screenshots)


# 全局实例
file_utils = FileUtils()