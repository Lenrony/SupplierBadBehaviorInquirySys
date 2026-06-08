# -*- coding: utf-8 -*-
"""
截图功能模块 - 页面截图和图片处理
"""

from pathlib import Path
from typing import Optional
from PIL import Image
from utils.logger import logger
from utils.file_utils import file_utils


class ScreenshotManager:
    """截图管理器"""

    @staticmethod
    def capture_and_save(
        page,
        output_dir: Path,
        site_name: str,
        supplier_name: str
    ) -> Optional[Path]:
        """
        截取页面并保存

        Args:
            page: Playwright页面对象
            output_dir: 输出目录
            site_name: 网站名称
            supplier_name: 供应商名称

        Returns:
            截图文件路径，失败返回None
        """
        try:
            # 生成文件名
            filename = file_utils.generate_screenshot_name(site_name, supplier_name)
            save_path = output_dir / filename

            # 等待页面加载完成
            page.wait_for_load_state("networkidle")

            # 执行截图
            page.screenshot(
                path=str(save_path),
                full_page=True,
                timeout=30000
            )

            logger.info(f"截图成功: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None

    @staticmethod
    def resize_image(image_path: Path, max_width: int = 800) -> bool:
        """
        调整图片大小

        Args:
            image_path: 图片路径
            max_width: 最大宽度

        Returns:
            是否成功
        """
        try:
            with Image.open(image_path) as img:
                # 计算缩放比例
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.LANCZOS)
                    img.save(image_path)
                    logger.debug(f"图片已缩放: {image_path}")

            return True

        except Exception as e:
            logger.error(f"图片缩放失败: {e}")
            return False

    @staticmethod
    def verify_image(image_path: Path) -> bool:
        """
        验证图片是否有效

        Args:
            image_path: 图片路径

        Returns:
            图片是否有效
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            logger.warning(f"图片验证失败: {image_path}")
            return False


# 全局实例
screenshot_manager = ScreenshotManager()