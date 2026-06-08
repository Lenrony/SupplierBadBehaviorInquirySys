# -*- coding: utf-8 -*-
"""
加密解密工具模块 - 用于密码和敏感信息的加密存储
"""

import base64
import keyring
from pathlib import Path
from cryptography.fernet import Fernet
from config import KEYRING_SERVICE, KEYRING_USERNAME, ENCRYPTION_KEY_FILE, get_app_data_dir
from utils.logger import logger


class CryptoManager:
    """加密管理器"""

    def __init__(self):
        self._fernet = None
        self._init_encryption()

    def _init_encryption(self):
        """初始化加密引擎"""
        try:
            # 尝试从文件读取密钥
            if ENCRYPTION_KEY_FILE.exists():
                with open(ENCRYPTION_KEY_FILE, 'rb') as f:
                    key = f.read()
            else:
                # 生成新密钥
                key = Fernet.generate_key()
                # 保存到文件
                with open(ENCRYPTION_KEY_FILE, 'wb') as f:
                    f.write(key)
                logger.info("生成新的加密密钥")

            self._fernet = Fernet(key)
        except Exception as e:
            logger.error(f"初始化加密引擎失败: {e}")
            # 使用keyring作为后备
            self._fernet = None

    def encrypt(self, plaintext: str) -> str:
        """
        加密字符串

        Args:
            plaintext: 明文密码

        Returns:
            Base64编码的加密字符串
        """
        if not plaintext:
            return ""

        try:
            if self._fernet:
                encrypted = self._fernet.encrypt(plaintext.encode('utf-8'))
                return base64.b64encode(encrypted).decode('utf-8')
            else:
                # 降级方案：直接返回（不推荐）
                return plaintext
        except Exception as e:
            logger.error(f"加密失败: {e}")
            return plaintext

    def decrypt(self, ciphertext: str) -> str:
        """
        解密字符串

        Args:
            ciphertext: Base64编码的加密字符串

        Returns:
            解密后的明文
        """
        if not ciphertext:
            return ""

        try:
            if self._fernet:
                decrypted = base64.b64decode(ciphertext.encode('utf-8'))
                return self._fernet.decrypt(decrypted).decode('utf-8')
            else:
                # 降级方案：直接返回
                return ciphertext
        except Exception as e:
            logger.error(f"解密失败: {e}")
            return ciphertext


class CredentialManager:
    """凭证管理器 - 使用keyring安全存储"""

    def __init__(self):
        self.crypto = CryptoManager()

    def save_credentials(self, username: str, password: str) -> bool:
        """
        保存登录凭证

        Args:
            username: 用户名
            password: 密码（将加密存储）

        Returns:
            是否保存成功
        """
        try:
            # 加密密码
            encrypted_password = self.crypto.encrypt(password)
            # 使用keyring存储
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, encrypted_password)
            # 用户名也加密存储
            encrypted_username = self.crypto.encrypt(username)
            keyring.set_password(KEYRING_SERVICE, "username", encrypted_username)
            logger.info("登录凭证已保存")
            return True
        except Exception as e:
            logger.error(f"保存凭证失败: {e}")
            # 尝试使用文件作为后备
            return self._save_to_file(username, password)

    def _save_to_file(self, username: str, password: str) -> bool:
        """后备存储方案"""
        try:
            cred_file = get_app_data_dir() / ".credentials"
            encrypted_pwd = self.crypto.encrypt(password)
            encrypted_usr = self.crypto.encrypt(username)
            with open(cred_file, 'w', encoding='utf-8') as f:
                f.write(f"{encrypted_usr}\n{encrypted_pwd}")
            logger.info("凭证已保存到文件（后备方案）")
            return True
        except Exception as e:
            logger.error(f"文件存储凭证失败: {e}")
            return False

    def load_credentials(self) -> tuple:
        """
        加载登录凭证

        Returns:
            (username, password) 元组，如果无保存则返回 (None, None)
        """
        try:
            encrypted_password = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            encrypted_username = keyring.get_password(KEYRING_SERVICE, "username")

            if encrypted_password and encrypted_username:
                username = self.crypto.decrypt(encrypted_username)
                password = self.crypto.decrypt(encrypted_password)
                logger.info("登录凭证已加载")
                return username, password
        except Exception as e:
            logger.warning(f"keyring加载失败，尝试文件: {e}")

        # 尝试从文件加载
        return self._load_from_file()

    def _load_from_file(self) -> tuple:
        """从文件加载凭证"""
        try:
            cred_file = get_app_data_dir() / ".credentials"
            if cred_file.exists():
                with open(cred_file, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    if len(lines) >= 2:
                        username = self.crypto.decrypt(lines[0])
                        password = self.crypto.decrypt(lines[1])
                        logger.info("从文件加载凭证成功")
                        return username, password
        except Exception as e:
            logger.error(f"文件加载凭证失败: {e}")

        return None, None

    def clear_credentials(self) -> bool:
        """清除保存的凭证"""
        try:
            try:
                keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
                keyring.delete_password(KEYRING_SERVICE, "username")
            except Exception:
                pass

            # 同时清除文件
            cred_file = get_app_data_dir() / ".credentials"
            if cred_file.exists():
                cred_file.unlink()

            logger.info("已清除保存的凭证")
            return True
        except Exception as e:
            logger.error(f"清除凭证失败: {e}")
            return False


# 全局实例
crypto_manager = CryptoManager()
credential_manager = CredentialManager()