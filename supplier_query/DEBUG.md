# 调试指南

## 一、启动调试模式

### 1.1 启用详细日志

修改 [main.py](file:///workspace/supplier_query/main.py#L1)，在 main() 函数前添加更详细的日志配置：

```python
import logging
from utils.logger import setup_logger

# 在 main() 开始处
logger = setup_logger()
logger.setLevel(logging.DEBUG)  # 设置为 DEBUG 级别
```

### 1.2 直接运行（不使用启动脚本）

```bash
cd /workspace/supplier_query
python3 -u main.py
```

## 二、模块调试

### 2.1 测试认证模块

```python
from core.auth import auth_manager

print("测试登录验证...")
result = auth_manager.login("admin", "admin123")
print(f"登录结果: {result}")
```

保存为 `test_auth.py`，运行：
```bash
python3 test_auth.py
```

### 2.2 测试加密模块

```python
from utils.crypto import crypto_manager, credential_manager

print("测试加密...")
encrypted = crypto_manager.encrypt("test123")
print(f"加密后: {encrypted}")

decrypted = crypto_manager.decrypt(encrypted)
print(f"解密后: {decrypted}")
```

### 2.3 测试文件工具

```python
from pathlib import Path
from utils.file_utils import file_utils
from config import get_app_data_dir

print("测试目录工具...")
print(f"应用数据目录: {get_app_data_dir()}")

print("测试创建输出文件夹...")
folder = file_utils.create_output_folder("测试供应商")
print(f"输出文件夹: {folder}")
```

### 2.4 测试浏览器控制

**注意**：需要先安装 Playwright 浏览器

```python
from core.browser import BrowserController

print("测试浏览器...")
with BrowserController() as browser:
    browser.initialize()
    result = browser.navigate_to("https://www.baidu.com")
    print(f"导航结果: {result}")
    print(f"页面标题: {browser.get_page_title()}")
```

## 三、断点调试

### 3.1 使用 pdb（内置调试器）

在需要断点的位置添加：

```python
import pdb
pdb.set_trace()  # 在这里设置断点
```

例如在 [query_engine.py](file:///workspace/supplier_query/core/query_engine.py#L1) 的 `query_single_site` 方法：

```python
def query_single_site(self, site: Dict):
    import pdb
    pdb.set_trace()  # 添加这里
    site_name = site["name"]
    ...
```

### 3.2 VS Code 调试配置

在项目根目录创建 `.vscode/launch.json`：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main",
            "type": "debugpy",
            "request": "launch",
            "program": "/workspace/supplier_query/main.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "/workspace/supplier_query"
            }
        }
    ]
}
```

## 四、常见调试点

### 4.1 检查依赖

```bash
cd /workspace/supplier_query
python3 -c "import tkinter; print('Tkinter OK')"
python3 -c "import PIL; print('Pillow OK')"
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
python3 -c "import docx; print('python-docx OK')"
python3 -c "import keyring; print('keyring OK')"
```

### 4.2 检查日志文件

```bash
# Linux
ls -la ~/.local/share/SupplierMisconductQuery/logs/
tail -f ~/.local/share/SupplierMisconductQuery/logs/app_$(date +%Y%m%d).log

# Windows (PowerShell)
dir "$env:APPDATA\SupplierMisconductQuery\logs"
Get-Content "$env:APPDATA\SupplierMisconductQuery\logs\app_$(Get-Date -Format yyyyMMdd).log" -Tail 50
```

### 4.3 清空配置重新开始

```bash
# Linux
rm -rf ~/.local/share/SupplierMisconductQuery/

# Windows (PowerShell)
Remove-Item -Recurse -Force "$env:APPDATA\SupplierMisconductQuery"
```

## 五、使用调试模式运行

### 5.1 创建调试启动脚本

在 [main.py](file:///workspace/supplier_query/main.py#L1) 中添加调试模式检测：

```python
import sys

# 在 main() 开始处
if "--debug" in sys.argv:
    logger.info("调试模式已启用")
    logger.setLevel(logging.DEBUG)
    import logging
    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)
```

然后这样运行：

```bash
python3 main.py --debug
```

### 5.2 添加详细调试输出

在关键位置添加详细日志，例如 [query_engine.py](file:///workspace/supplier_query/core/query_engine.py#L1)：

```python
logger.debug(f"准备导航到: {site_url}")
# ...
logger.debug(f"页面加载状态: {self._browser._page.url}")
# ...
logger.debug(f"截图保存路径: {save_path}")
```

## 六、单独测试查询引擎

创建 `test_query.py`：

```python
from pathlib import Path
from core.query_engine import create_query_engine
from config import get_default_download_dir

def test_query():
    print("=" * 60)
    print("测试查询引擎")
    print("=" * 60)
    
    output_dir = get_default_download_dir() / "test_query"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"输出目录: {output_dir}")
    
    query_engine = create_query_engine(
        supplier_name="测试供应商",
        credit_code="911100000000000000",
        is_engineering=False,
        output_dir=output_dir
    )
    
    print("开始查询...")
    results = query_engine.execute()
    
    print(f"\n查询完成，共 {len(results)} 个结果")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.site_name}")
        print(f"   URL: {result.site_url}")
        print(f"   状态: {result.status}")
        if result.screenshot_path:
            print(f"   截图: {result.screenshot_path.name}")
        if result.error_message:
            print(f"   错误: {result.error_message}")

if __name__ == "__main__":
    test_query()
```

运行：
```bash
python3 test_query.py
```

## 七、常见调试问题

| 问题 | 排查步骤 |
|------|---------|
| 程序启动失败 | 1. 检查 Python 版本<br>2. 检查 Tkinter 是否安装<br>3. 查看日志文件 |
| 浏览器初始化失败 | 1. 运行 `playwright install chromium`<br>2. 确认浏览器可访问<br>3. 检查内存是否充足 |
| 页面加载超时 | 1. 检查网络连接<br>2. 增加超时时间（config.py）<br>3. 手动测试站点可访问性 |
| 报告生成失败 | 1. 检查输出目录权限<br>2. 检查 Pillow/python-docx 安装<br>3. 检查截图是否存在 |

## 八、性能分析

使用 cProfile 分析性能：

```bash
python3 -m cProfile -s cumtime main.py > profile.log
head -50 profile.log
```

## 九、获取帮助

如仍有问题，请：
1. 查看日志文件
2. 检查常见问题文档 [TROUBLESHOOTING.md](file:///workspace/supplier_query/TROUBLESHOOTING.md)
3. 保存完整错误信息和日志