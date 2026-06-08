# 常见问题排查指南

## 一、安装问题

### 1.1 Python 未找到

**症状**: 运行脚本时报错 "未检测到Python"

**解决方案**:
- Windows: 从 https://www.python.org/downloads/ 下载并安装 Python 3.8+
- Linux: 使用系统包管理器安装
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3 python3-pip

  # CentOS/RHEL
  sudo yum install python3 python3-pip
  ```

### 1.2 Tkinter 缺失

**症状**: 程序无法启动，报错 "no module named 'tkinter'"

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-pil python3-pil.imagetk

# CentOS/RHEL
sudo yum install python3-tkinter

# Fedora
sudo dnf install python3-tkinter
```

### 1.3 依赖安装失败

**症状**: pip install 报错

**解决方案**:
1. 升级 pip
   ```bash
   pip3 install --upgrade pip
   ```

2. 使用镜像源
   ```bash
   pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

### 1.4 Playwright 浏览器安装失败

**症状**: 报错 "Browser not installed"

**解决方案**:
```bash
# 安装 Chromium
playwright install chromium

# 或安装 Firefox
playwright install firefox
```

## 二、运行问题

### 2.1 窗口显示异常

**症状**: 界面显示不完整或乱码

**解决方案**:
1. 设置环境变量
   ```bash
   export LANG=zh_CN.UTF-8
   export LC_ALL=zh_CN.UTF-8
   ```

2. 安装中文字体
   ```bash
   # Ubuntu/Debian
   sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
   ```

### 2.2 登录失败

**症状**: 输入正确密码仍无法登录

**解决方案**:
1. 清除保存的凭证
   ```bash
   # Windows
   del %APPDATA%\SupplierMisconductQuery\.credentials

   # Linux
   rm ~/.local/share/SupplierMisconductQuery/.credentials
   ```

2. 使用默认账号登录: admin / admin123

### 2.3 程序无响应

**症状**: 点击按钮后程序卡死

**解决方案**:
- 这是正常现象，查询过程较慢请耐心等待
- 可查看日志了解当前进度
- 如长时间无响应，可尝试重启程序

### 2.4 截图不完整

**症状**: 截取的页面只有空白或部分内容

**解决方案**:
1. 增加页面等待时间
2. 检查网络连接
3. 确认目标站点是否正常访问

## 三、查询问题

### 3.1 站点访问失败

**症状**: 某个站点无法访问

**可能原因**:
1. 网络问题 - 检查网络连接
2. 站点维护 - 稍后重试
3. IP被封 - 等待后重试

**解决方案**:
- 程序会自动重试2次
- 可手动打开浏览器测试站点是否可访问
- 检查系统代理设置

### 3.2 验证码问题

**症状**: 程序停留在验证码页面

**解决方案**:
1. 程序会弹出提示窗口
2. 手动在浏览器中完成验证
3. 点击"已完成验证"按钮继续

### 3.3 页面加载超时

**症状**: 报错 "页面加载超时"

**解决方案**:
1. 检查网络速度
2. 目标站点可能较慢，等待后重试
3. 暂时跳过该站点

### 3.4 特定站点无法查询

**症状**: 只能查询部分站点

**解决方案**:
- 确认是否选择了正确的"是否工程类"选项
- 工程类供应商应选择"是"
- 非工程类供应商选择"否"

## 四、文件问题

### 4.1 无法创建输出目录

**症状**: 报错 "Permission denied" 或 "无法创建目录"

**解决方案**:
1. 检查目标目录是否有写入权限
2. 选择其他目录作为输出路径
3. Windows: 右键文件夹 -> 属性 -> 安全 -> 编辑权限
4. Linux: `chmod 755 target_directory`

### 4.2 文件名乱码

**症状**: 生成的截图或文档名显示乱码

**解决方案**:
1. 确保终端和文件系统使用 UTF-8 编码
2. 供应商名称避免使用特殊字符
3. 报告使用项目自带字体，无乱码问题

### 4.3 Word 报告生成失败

**症状**: 查询完成但报告未生成

**解决方案**:
1. 检查 python-docx 是否正确安装
   ```bash
   pip3 show python-docx
   ```
2. 确认输出目录有写入权限
3. 查看日志中的具体错误信息

### 4.4 图片无法插入 Word

**症状**: 报告中图片位置为空白或错误

**解决方案**:
1. 确保 Pillow 库正确安装
   ```bash
   pip3 show Pillow
   ```
2. 确认截图文件未损坏
3. 检查磁盘空间是否充足

## 五、性能问题

### 5.1 查询速度慢

**优化建议**:
1. 确保网络连接稳定
2. 关闭其他占用带宽的程序
3. 减少同时运行的程序数量

### 5.2 内存占用高

**优化建议**:
1. 定期重启程序清理内存
2. 及时清理历史查询结果
3. 适当减少截图分辨率

## 六、跨平台问题

### 6.1 Windows 和 Linux 行为不一致

**说明**: 由于系统差异，部分细节可能不同，但核心功能一致。

### 6.2 国产系统兼容性问题

**常见问题**:
1. 字体显示异常 - 安装中文字体包
2. 文件路径问题 - 程序使用 pathlib 自动处理
3. 权限问题 - 使用具有写权限的目录

### 6.3 浏览器选择

- Windows: 自动使用系统 Chrome
- Linux: 优先使用 Chromium，备选 Firefox
- 如需切换浏览器，修改 config.py 中的配置

## 七、日志获取

### 7.1 日志文件位置

```
# Windows
%APPDATA%\SupplierMisconductQuery\logs\

# Linux
~/.local/share/SupplierMisconductQuery/logs/
```

### 7.2 查看实时日志

```bash
# Linux
tail -f ~/.local/share/SupplierMisconductQuery/logs/app_YYYYMMDD.log

# Windows
type %APPDATA%\SupplierMisconductQuery\logs\app_YYYYMMDD.log
```

## 八、联系我们

如遇到本文档未涵盖的问题，请：

1. 查看程序日志文件
2. 记录详细的错误信息
3. 记录您的操作系统版本
4. 联系技术支持团队