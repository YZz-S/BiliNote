# BiliNote Release Notes

> Branch: `my_dev` | Range: `e276afc..bd8f2fd` | 60 commits | 59 files changed

---

## Highlights

### GUI 启动器（全新）

新增 BiliNote GUI 启动器，支持一键启动前后端服务、进程状态监控、端口检查、日志查看和系统依赖检测，告别手动命令行启动。

### 长视频智能总结

GPT 总结能力全面升级：超长转录文本自动分段处理，遇到 413 错误自动降级重试，模型不支持图像时自动回退纯文本模式。大视频不再"静默失败"。

### 导出原文与字幕

支持将原始转录导出为 Markdown 文件和 `.srt` 字幕文件，在笔记页面一键下载。

### 任务失败自动恢复

当任务返回成功但结果文件缺失时，后端会尝试从缓存自动恢复。前端轮询也增加了对"成功但结果不完整"场景的兜底处理，配合浏览器通知提醒任务状态变化。

### B 站下载稳定性大幅提升

下载器补充完整请求头、支持 Cookie 配置文件、`b23.tv` 短链自动解析、412 反爬错误明确提示，B 站资源抓取成功率显著提高。

### CUDA 环境检查与 Whisper 转写器健壮性

新增 CUDA / Python / PyTorch / cuDNN 版本检查脚本，Whisper 转写器在 CUDA 不可用时自动回退 CPU 模式，GPU 环境问题不再导致启动失败。

### 模型供应商管理

支持删除模型供应商和已启用模型，供应商编辑页面操作更完整。

---

## What's New

### Features

- **GUI 启动器**: 新增 `gui_launcher.py` / `start_gui.py` 及 `modules/` 模块，支持图形化前后端管理
- **启动脚本**: 新增 `start_all.bat` / `start_all.ps1` / `start_all.sh` / `start_bilinote.bat`，支持 conda 虚拟环境
- **长文本分段总结**: GPT 输入超长时自动分段处理，413 错误自动降级重试
- **导出原文 .md**: 可将原始转录导出为 Markdown 文件 (`buildMarkdownFromTranscript`)
- **导出原文 .srt**: 可将原始转录导出为 SRT 字幕文件 (`buildSrtFromTranscript`)
- **浏览器通知**: 任务成功/失败时主动推送浏览器通知 (`notifyTaskSuccess` / `notifyTaskFailed`)
- **模型供应商删除**: 后端新增 `delete_provider` 接口，前端 `Form` 组件支持删除操作
- **B 站 Cookie 增强**: 支持从 `CookieConfigManager` 读取 Cookie，支持 `cookiefile` / Netscape 格式
- **B 站请求头补全**: 下载器补充完整 HTTP 请求头，提升反爬能力
- **B 站短链解析**: 针对 `b23.tv` 短链增加真实地址解析
- **封面保存优化**: 封面图保存到静态目录，优化截图生成逻辑
- **任务状态完善**: 完善任务状态定义、轮询流程和失败处理逻辑
- **缓存恢复**: 结果文件缺失时自动从缓存恢复
- **CUDA 环境检查**: 新增 `check_cuda_pytorch_versions.py` 脚本和 `env_checker.py` CUDA 检查
- **Whisper CPU 回退**: CUDA 不可用时自动切换 CPU 模式

### Bug Fixes

- 修复 `MarkdownViewer` 图片路径拼接问题，相对路径正确拼接 baseURL
- 修复文件上传超时和内存问题
- 修复视频帧提取的健壮性和错误处理
- 修复端口配置不一致问题，统一后端默认端口为 8483
- 修复 GPT 输入长度限制不足导致的错误
- 增强 B 站下载器反爬能力，修复短链解析
- 前端 pnpm lockfile 跟踪及 icon 依赖对齐
- 升级依赖以修复安全漏洞 (starlette, h11, urllib3, tornado, pillow 等)

### Dependencies

**Backend (Python):**
- h11: 0.14.0 → 0.16.0
- starlette: 0.46.1 → 0.49.1
- fonttools: 4.58.4 → 4.61.0
- urllib3: 2.3.0 → 2.6.3
- filelock: 3.18.0 → 3.20.3
- weasyprint: 65.1 → 68.0
- protobuf: 6.30.2 → 6.33.5
- yt-dlp: 2025.3.31 → 2026.2.21
- tornado: 6.4.2 → 6.5.5
- pillow: 11.0.0 → 12.2.0
- python-multipart: 0.0.20 → 0.0.26
- aiohttp: 3.11.16 → 3.13.4
- orjson: 3.10.16 → 3.11.6
- requests: 2.32.3 → 2.33.0
- markdown: 3.8 → 3.8.1
- pygments: 2.19.1 → 2.20.0
- brotli: 1.1.0 → 1.2.0

**Frontend / Tauri:**
- slab (Rust crate)
- bytes (Rust crate)
- time (Rust crate)
- Tauri 核心及插件版本更新

### Documentation

- README 补充项目历史、差异说明、Cookie 配置、环境变量说明
- 新增 CUDA / Python / PyTorch / cuDNN 版本对应关系文档
- 新增超长视频转录摘要处理方案文档
- 新增 HTTP 412 错误操作说明文档
- 新增 GUI 启动器说明文档 (`GUI_LAUNCHER_README.md`)
- 新增提示词模板管理和 GUI 可视化功能说明
- 补充 `FFMPEG_BIN_PATH` 环境变量示例
- 新增任务状态流转与缓存恢复测试用例

---

## Upgrade Notes

- 后端默认端口已统一为 `8483`，请检查本地配置是否一致
- 前端现使用 `pnpm-lock.yaml` 管理依赖，请使用 `pnpm install` 安装
- CUDA 环境用户可运行 `check_cuda_pytorch_versions.py` 检查环境兼容性
