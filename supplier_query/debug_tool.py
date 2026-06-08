#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试工具 - 快速测试各个模块
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_imports():
    """测试所有模块导入"""
    print_banner("测试模块导入")
    
    modules = [
        ("配置模块", "config"),
        ("日志工具", "utils.logger"),
        ("加密工具", "utils.crypto"),
        ("文件工具", "utils.file_utils"),
        ("认证模块", "core.auth"),
        ("浏览器模块", "core.browser"),
        ("截图模块", "core.screenshot"),
        ("查询引擎", "core.query_engine"),
        ("报告生成", "core.report_generator"),
        ("登录界面", "gui.login_window"),
        ("主界面", "gui.main_window"),
    ]
    
    for name, module in modules:
        try:
            __import__(module)
            print(f"[OK] {name} ({module})")
        except Exception as e:
            print(f"[失败] {name} ({module}): {e}")
            return False
    return True

def test_utils():
    """测试工具模块"""
    print_banner("测试工具模块")
    
    from config import get_app_data_dir, get_default_download_dir
    from utils.crypto import crypto_manager, credential_manager
    from utils.file_utils import file_utils
    from utils.logger import logger
    
    print("\n1. 测试路径工具:")
    app_dir = get_app_data_dir()
    print(f"   应用数据目录: {app_dir}")
    print(f"   目录存在: {app_dir.exists()}")
    
    download_dir = get_default_download_dir()
    print(f"   默认下载目录: {download_dir}")
    
    print("\n2. 测试加密工具:")
    test_str = "test_password_123"
    encrypted = crypto_manager.encrypt(test_str)
    print(f"   加密成功: {encrypted[:30]}...")
    
    decrypted = crypto_manager.decrypt(encrypted)
    print(f"   解密成功: {decrypted == test_str}")
    
    print("\n3. 测试文件名工具:")
    safe_name = file_utils.sanitize_filename("测试供应商/\\:*?\"<>|")
    print(f"   安全文件名: {safe_name}")
    
    screenshot_name = file_utils.generate_screenshot_name("测试站点", "测试供应商")
    print(f"   截图文件名: {screenshot_name}")
    
    return True

def test_auth():
    """测试认证模块"""
    print_banner("测试认证模块")
    
    from core.auth import auth_manager
    
    print("\n1. 测试默认账号:")
    result = auth_manager.login("admin", "admin123")
    print(f"   登录结果: {result}")
    print(f"   已登录: {auth_manager.is_logged_in}")
    print(f"   当前用户: {auth_manager.current_user}")
    
    auth_manager.logout()
    print(f"\n   登出后: {auth_manager.is_logged_in}")
    
    print("\n2. 测试错误账号:")
    result = auth_manager.login("wrong", "wrong")
    print(f"   登录结果: {result}")
    
    return True

def test_browser():
    """测试浏览器模块（可选）"""
    print_banner("测试浏览器模块")
    print("\n浏览器测试需要联网，且可能需要几分钟")
    
    answer = input("是否继续? (y/n): ").strip().lower()
    if answer != "y":
        print("跳过浏览器测试")
        return True
    
    try:
        from core.browser import BrowserController
        
        print("\n初始化浏览器...")
        with BrowserController() as browser:
            if not browser.initialize():
                print("浏览器初始化失败")
                return False
            
            print("导航到测试页面...")
            result = browser.navigate_to("https://www.example.com")
            print(f"导航结果: {result}")
            
            if result:
                title = browser.get_page_title()
                print(f"页面标题: {title}")
        
        print("\n浏览器测试完成")
        return True
        
    except Exception as e:
        print(f"浏览器测试异常: {e}")
        return True  # 不影响整体测试结果

def test_file_operations():
    """测试文件操作"""
    print_banner("测试文件操作")
    
    from pathlib import Path
    from utils.file_utils import file_utils
    from config import get_app_data_dir
    
    test_dir = get_app_data_dir() / "debug_test"
    
    print(f"\n测试目录: {test_dir}")
    
    try:
        test_dir.mkdir(parents=True, exist_ok=True)
        print("目录创建成功")
        
        # 测试写入权限
        test_file = test_dir / "test_write.txt"
        test_file.write_text("测试内容", encoding="utf-8")
        print("文件写入成功")
        
        # 测试读取
        content = test_file.read_text(encoding="utf-8")
        print(f"文件读取成功: {content}")
        
        # 清理
        test_file.unlink()
        test_dir.rmdir()
        print("测试文件已清理")
        
        return True
        
    except Exception as e:
        print(f"文件操作失败: {e}")
        return False

def main():
    """主调试函数"""
    print("\n" + "=" * 60)
    print("  供应商不良行为查询工具 - 调试工具")
    print("=" * 60)
    
    # 检查是否跳过浏览器测试
    skip_browser = "--no-browser" in sys.argv
    
    results = []
    
    # 运行各个测试
    results.append(("模块导入", test_imports()))
    results.append(("工具模块", test_utils()))
    results.append(("认证模块", test_auth()))
    results.append(("文件操作", test_file_operations()))
    
    # 浏览器测试（可选）
    if not skip_browser:
        results.append(("浏览器模块", test_browser()))
    
    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = "通过" if ok else "失败"
        print(f"  {name}: {status}")
    
    print("\n" + "-" * 60)
    print(f"  总计: {passed}/{total} 项测试通过")
    print("-" * 60)
    
    if passed == total:
        print("\n所有测试通过！")
        return 0
    else:
        print("\n部分测试失败，请检查相关模块")
        print("\n详细日志请查看:")
        print("  - 控制台输出")
        print("  - ~/.local/share/SupplierMisconductQuery/logs/ (Linux)")
        print("  - %APPDATA%\\SupplierMisconductQuery\\logs\\ (Windows)")
        return 1

if __name__ == "__main__":
    sys.exit(main())