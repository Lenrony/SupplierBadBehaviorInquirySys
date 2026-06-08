# -*- coding: utf-8 -*-
"""
配置文件 - 包含所有站点URL和系统配置
"""

from pathlib import Path
import sys
import os

# ============ 应用配置 ============
APP_NAME = "供应商不良行为查询工具"
APP_VERSION = "1.0.0"

# ============ 站点配置 ============

# 通用查询站点（所有供应商必查）
GENERAL_SITES = [
    {
        "name": "中国裁判文书网",
        "url": "https://wenshu.court.gov.cn/",
        "xpath": "//input[@id='searchText']",  # 搜索框XPath
        "description": "查询司法裁判文书"
    },
    {
        "name": "信用中国",
        "url": "https://www.creditchina.gov.cn/",
        "xpath": "//input[@id='search_keyword']",
        "description": "查询信用记录"
    },
    {
        "name": "中国政府采购网",
        "url": "https://www.ccgp.gov.cn/",
        "xpath": "//input[@id='keyword']",
        "description": "查询政府采购不良行为"
    },
    {
        "name": "国家企业信用信息公示系统",
        "url": "https://www.gsxt.gov.cn/",
        "xpath": "//input[@id='keyword']",
        "description": "查询企业信用信息"
    },
    {
        "name": "烟草行业采购管理信息系统",
        "url": "https://ec.yn/tobacco/",  # 内部URL，后续可能调整
        "xpath": "//input[@type='text']",
        "description": "查询烟草行业采购记录"
    },
]

# 工程类专属站点（仅工程类供应商查询）
ENGINEERING_SITES = [
    {
        "name": "全国建筑市场监管公共服务平台",
        "url": "https://jzsc.mohurd.gov.cn/",
        "xpath": "//input[@id='keyword']",
        "description": "查询建筑市场行为记录"
    },
    {
        "name": "广东省建筑市场监管公共服务平台",
        "url": "https://210.76.82.21/",  # 可能需要更新
        "xpath": "//input[@type='text']",
        "description": "查询广东省建筑市场记录"
    },
]

# ============ 系统路径配置 ============

def get_app_data_dir():
    """获取应用数据目录（跨平台）"""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        # Linux 国产系统
        base = Path.home() / ".local" / "share"
    app_dir = base / "SupplierMisconductQuery"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def get_log_dir():
    """获取日志目录"""
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def get_default_download_dir():
    """获取默认下载/存储目录"""
    if sys.platform == "win32":
        default_dir = Path(os.environ.get("USERPROFILE", Path.home())) / "Documents" / "供应商查询报告"
    else:
        default_dir = Path.home() / "文档" / "供应商查询报告"
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir

# ============ 浏览器配置 ============

def get_browser_config():
    """获取浏览器配置（跨平台适配）"""
    if sys.platform == "win32":
        # Windows: 使用Chrome
        return {
            "browser_type": "chromium",
            "channel": "chrome",  # 使用系统已安装的Chrome
            "headless": False,
        }
    else:
        # 国产Linux系统: 优先Chromium，备选Firefox
        return {
            "browser_type": "chromium",
            "channel": None,
            "headless": False,
        }

# ============ 时间配置 ============

# 页面加载超时（毫秒）
PAGE_LOAD_TIMEOUT = 30000

# 站点间延时范围（秒）
DELAY_MIN = 2
DELAY_MAX = 5

# 重试次数
MAX_RETRIES = 2

# ============ Word文档配置 ============

# Word文档页面尺寸（英寸）
WORD_PAGE_WIDTH = 6.3  # A4宽度减去边距
WORD_PAGE_HEIGHT = 9.0

# 图片最大宽度（英寸）
IMAGE_MAX_WIDTH = 5.5

# ============ 加密配置 ============

# keyring服务名称
KEYRING_SERVICE = "SupplierMisconductQuery"
KEYRING_USERNAME = "user_credentials"

# 加密密钥文件
ENCRYPTION_KEY_FILE = get_app_data_dir() / ".encryption_key"