# -*- coding: utf-8 -*-
"""
认证模块 - 处理用户登录验证
"""

import hashlib
from typing import Optional
from utils.crypto import credential_manager
from utils.logger import logger


class AuthManager:
    """认证管理器"""

    # 默认账号密码（可根据需要修改）
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "admin123"

    def __init__(self):
        self._current_user: Optional[str] = None
        self._is_logged_in = False

    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希（单向）"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, input_password: str, stored_hash: str) -> bool:
        """验证密码"""
        return self.hash_password(input_password) == stored_hash

    def login(self, username: str, password: str) -> bool:
        """
        用户登录验证

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录是否成功
        """
        try:
            # 简单验证：用户名和密码都不为空
            if not username or not password:
                logger.warning("用户名或密码为空")
                return False

            # 使用默认账号验证（或可扩展为数据库验证）
            input_hash = self.hash_password(password)

            # 默认账号验证
            if username == self.DEFAULT_USERNAME:
                expected_hash = self.hash_password(self.DEFAULT_PASSWORD)
                if input_hash == expected_hash:
                    self._current_user = username
                    self._is_logged_in = True
                    logger.info(f"用户登录成功: {username}")
                    return True

            # 如果设置了自定义密码，则验证
            stored_password = credential_manager.load_credentials()[1]
            if stored_password:
                # 验证输入密码
                if password == stored_password:
                    self._current_user = username
                    self._is_logged_in = True
                    logger.info(f"用户登录成功: {username}")
                    return True

            logger.warning(f"用户登录失败: {username}")
            return False

        except Exception as e:
            logger.error(f"登录验证异常: {e}")
            return False

    def logout(self):
        """用户登出"""
        self._current_user = None
        self._is_logged_in = False
        logger.info("用户已登出")

    @property
    def is_logged_in(self) -> bool:
        """是否已登录"""
        return self._is_logged_in

    @property
    def current_user(self) -> Optional[str]:
        """当前登录用户"""
        return self._current_user

    def save_credentials(self, username: str, password: str) -> bool:
        """保存登录凭证"""
        return credential_manager.save_credentials(username, password)

    def load_saved_credentials(self) -> tuple:
        """加载已保存的登录凭证"""
        return credential_manager.load_credentials()

    def clear_credentials(self):
        """清除保存的凭证"""
        credential_manager.clear_credentials()


# 全局实例
auth_manager = AuthManager()