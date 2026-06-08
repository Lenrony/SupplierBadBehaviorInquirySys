#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速诊断工具 - 不依赖第三方库
用于检查环境配置和基础模块
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_python():
    """检查 Python 环境"""
    print_header("Python 环境检查")
    print(f"  Python 版本: {sys.version}")
    
    version_ok = sys.version_info >= (3, 8)
    print(f"  版本要求: 3.8+ - {'✓ 满足' if version_ok else '✗ 不满足'}")
    
    print(f"  操作系统: {platform.system()} {platform.release()}")
    print(f"  架构: {platform.machine()}")
    print(f"  编码: {sys.getdefaultencoding()}")
    
    return version_ok

def check_filesystem():
    """检查文件系统"""
    print_header("文件系统检查")
    
    app_dir = Path.home() / ".local" / "share" / "SupplierMisconductQuery"
    if platform.system() == "Windows":
        app_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "SupplierMisconductQuery"
    
    print(f"  应用数据目录: {app_dir}")
    
    try:
        app_dir.mkdir(parents=True, exist_ok=True)
        print(f"  目录创建: ✓ 成功")
        
        test_file = app_dir / "test_write.tmp"
        test_file.write_text("test", encoding="utf-8")
        test_file.read_text(encoding="utf-8")
        test_file.unlink()
        print(f"  读写权限: ✓ 正常")
        return True
        
    except Exception as e:
        print(f"  读写权限: ✗ 失败 - {e}")
        return False

def check_encoding():
    """检查编码设置"""
    print_header("编码检查")
    
    test_str = "供应商不良行为查询工具 - 中文字符测试"
    print(f"  测试字符串: {test_str}")
    
    try:
        # 测试编码/解码
        encoded = test_str.encode("utf-8")
        decoded = encoded.decode("utf-8")
        print(f"  UTF-8 编码: ✓ 正常")
        return decoded == test_str
    except Exception as e:
        print(f"  UTF-8 编码: ✗ 失败 - {e}")
        return False

def check_pathlib():
    """检查 pathlib 功能"""
    print_header("pathlib 检查")
    
    try:
        # 各种路径操作测试
        home = Path.home()
        print(f"  主目录: ✓ {home}")
        
        test_path = home / "test" / "dir" / "file.txt"
        print(f"  路径拼接: ✓ {test_path}")
        
        print(f"  父目录: ✓ {test_path.parent}")
        print(f"  文件名: ✓ {test_path.name}")
        
        abs_path = Path(".").resolve()
        print(f"  绝对路径: ✓ {abs_path}")
        
        return True
    except Exception as e:
        print(f"  pathlib: ✗ 失败 - {e}")
        return False

def check_std_modules():
    """检查标准库"""
    print_header("标准库检查")
    
    std_modules = [
        ("tkinter", "Tkinter GUI"),
        ("logging", "日志模块"),
        ("sqlite3", "数据库"),
        ("hashlib", "哈希加密"),
        ("subprocess", "子进程"),
        ("threading", "多线程"),
        ("datetime", "日期时间"),
        ("json", "JSON处理"),
    ]
    
    all_ok = True
    for mod, desc in std_modules:
        try:
            __import__(mod)
            print(f"  ✓ {mod:<15} - {desc}")
        except ImportError:
            print(f"  ✗ {mod:<15} - {desc} (缺失)")
            all_ok = False
    
    return all_ok

def check_optional_dependencies():
    """检查可选依赖（不报错）"""
    print_header("第三方依赖检查")
    
    optional_modules = [
        ("keyring", "密码加密存储"),
        ("cryptography", "加密库"),
        ("playwright", "网页自动化"),
        ("PIL", "图片处理"),
        ("docx", "Word文档生成"),
    ]
    
    print("  (这些依赖需要通过 pip install -r requirements.txt 安装)")
    print()
    
    missing = []
    for mod, desc in optional_modules:
        try:
            if mod == "docx":
                __import__("docx")
            elif mod == "PIL":
                __import__("PIL.Image")
            else:
                __import__(mod)
            print(f"  ✓ {mod:<15} - {desc}")
        except ImportError:
            print(f"  ✗ {mod:<15} - {desc} (未安装)")
            missing.append(mod)
    
    return missing

def suggest_install(missing_modules):
    """给出安装建议"""
    if not missing_modules:
        return
    
    print_header("安装建议")
    print("\n运行以下命令安装依赖:")
    print("  pip install -r requirements.txt")
    
    if "tkinter" in missing_modules:
        print("\nTkinter 是 Python 自带的，但某些系统需要额外安装:")
        if platform.system() == "Linux":
            print("  Ubuntu/Debian: sudo apt-get install python3-tk")
            print("  统信UOS/银河麒麟: 同上或使用软件中心")
        elif platform.system() == "Windows":
            print("  Windows: 重新运行 Python 安装程序，勾选 'tcl/tk and IDLE'")

def show_project_structure():
    """显示项目结构"""
    print_header("项目结构")
    
    project_root = Path(__file__).parent
    print(f"\n项目根目录: {project_root}\n")
    
    important_files = [
        "main.py",
        "config.py",
        "requirements.txt",
        "README.md",
        "DEBUG.md",
        "start_windows.bat",
        "start_linux.sh",
        "install_deps.sh",
    ]
    
    for f in important_files:
        f_path = project_root / f
        exists = f_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {f}")
    
    print()
    
    # 显示目录结构
    dirs = ["core", "gui", "utils"]
    for d in dirs:
        d_path = project_root / d
        exists = d_path.exists() and d_path.is_dir()
        status = "✓" if exists else "✗"
        print(f"  {status} {d}/")
        
        if exists:
            files = list(d_path.glob("*.py"))
            for py_file in files:
                print(f"      - {py_file.name}")

def main():
    """主诊断函数"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "供应商不良行为查询工具 - 快速诊断" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # 运行检查
    python_ok = check_python()
    fs_ok = check_filesystem()
    enc_ok = check_encoding()
    path_ok = check_pathlib()
    std_ok = check_std_modules()
    missing_modules = check_optional_dependencies()
    
    # 总结
    print_header("诊断总结")
    
    basic_ok = python_ok and fs_ok and enc_ok and path_ok and std_ok
    
    if basic_ok:
        print("\n  ✓ 基础环境检查通过")
    else:
        print("\n  ✗ 基础环境有问题，请修复以上错误")
    
    if not missing_modules:
        print("  ✓ 所有第三方依赖已安装")
    else:
        print(f"  ✗ 缺少 {len(missing_modules)} 个第三方依赖")
        suggest_install(missing_modules)
    
    # 显示项目结构
    show_project_structure()
    
    # 下一步建议
    print_header("下一步")
    print()
    
    if basic_ok and not missing_modules:
        print("  环境已就绪！")
        print("  运行: python3 main.py")
        print("  或:   ./start_linux.sh (Linux) / start_windows.bat (Windows)")
    else:
        print("  请先完成依赖安装，再运行:")
        print("  1. pip install -r requirements.txt")
        print("  2. playwright install chromium")
        print("  3. python3 debug_tool.py")
    
    print()
    print("  详细调试指南: 查看 DEBUG.md")
    print("  常见问题: 查看 TROUBLESHOOTING.md")
    print()

if __name__ == "__main__":
    main()