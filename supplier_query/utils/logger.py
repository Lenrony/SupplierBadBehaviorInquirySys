# -*- coding: utf-8 -*-
"""
日志工具模块 - 跨平台统一日志格式
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from config import get_log_dir


class CrossPlatformFormatter(logging.Formatter):
    """跨平台日志格式化器"""

    def __init__(self):
        super().__init__(
            fmt='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def format(self, record):
        # 确保中文兼容性
        record.msg = str(record.msg)
        return super().format(record)


def setup_logger(name: str = "SupplierMisconductQuery") -> logging.Logger:
    """
    设置并返回日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        配置好的Logger对象
    """
    logger = logging.getLogger(name)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CrossPlatformFormatter())

    # 文件处理器
    log_file = get_log_dir() / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(
        log_file,
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(CrossPlatformFormatter())

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 全局日志实例
logger = setup_logger()