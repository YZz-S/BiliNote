# Changelog

## 范围说明

- 当前分支：`my_dev`
- 当前提交：`bd8f2fd12f637a187b701bedb4df42284fd6f564`
- 对比方式：基于提交快照对比 `git diff <commit>..HEAD`，而不是仅按线性提交链整理
- 说明：`48e7981de4254fbc4f7078a5bc08cf6c716936bd` 与 `e276afcb7e4817b2519d2d47ae3c91ed71accc16` 在当前历史中并不是单纯的前后顺承关系，因此以下内容以“基线版本快照”对“当前 HEAD 快照”的差异为准
- 本文不包含当前工作区未提交文件与同步冲突文件，仅统计已进入当前 `HEAD` 的改动

## 一、从 `e276afcb7e4817b2519d2d47ae3c91ed71accc16` 到当前 HEAD 的改动

快照统计：

- 变更文件数：59
- 代码变更量：约 `20526` 行新增，`1107` 行删除

### 1. 启动与运维能力增强

- 新增一套本地启动脚本：`start_all.bat`、`start_all.ps1`、`start_all.sh`、`start_bilinote.bat`
- 新增 GUI 启动器相关实现：`gui_launcher.py`、`start_gui.py`、`modules/`
- GUI 启动器支持前后端一键启动、进程状态查看、端口检查、配置读取、日志监控、系统依赖检测
- 补充 GUI 启动器文档、PRD 和架构说明，方便后续维护与交接

### 2. Bilibili 下载链路增强

- 下载器补充更完整的 B 站请求头，提升资源抓取稳定性
- 支持从 `CookieConfigManager` 读取并应用 B 站 Cookie
- 支持 `cookiefile` / Netscape 格式 Cookie 文件，降低登录态丢失造成的失败率
- 针对 `b23.tv` 短链增加真实地址解析，减少短链阶段的反爬拦截
- 对 HTTP 412 等典型反爬错误补充更明确的报错与操作提示
- 优化封面保存到静态目录和截图生成逻辑，便于前端直接展示

### 3. 长视频与 GPT 总结能力增强

- GPT 输入长度控制从简单截断，扩展为更稳健的超长文本分段总结逻辑
- 遇到 `413 Request Entity Too Large` 时，会自动降级为分块重试，而不是直接失败
- 当模型不支持图像输入时，可自动降级为纯文本总结模式
- 优化连通性测试逻辑，测试时会结合已保存模型做更合理的候选检查
- 完善异常捕获与提示，减少大视频、长转录场景下的“静默失败”

### 4. 任务状态、失败处理与缓存恢复增强

- 完善任务状态定义与轮询流程，前后端状态协同更完整
- 当任务返回成功但结果文件缺失时，后端会尝试从缓存自动恢复结果
- 当结果为空、结果不完整或保存失败时，会主动标记任务失败并记录原因
- 前端轮询增加对成功但结果不完整场景的兜底处理
- 前端在轮询失败、任务失败时补充更明确的失败分支和状态更新
- 新增针对任务状态流转与缓存恢复的测试用例

### 5. 前端导出与通知体验增强

- 新增原始转录导出能力，可导出为原文 Markdown
- 新增原始转录导出能力，可导出为 `.srt` 字幕文件
- `MarkdownHeader` 新增“导出原文 .md / 导出原文 .srt”操作入口
- 新增浏览器通知能力，任务成功或失败时可主动提醒
- 修复 `MarkdownViewer` 图片路径拼接问题，改善笔记内容展示稳定性

### 6. 模型供应商与模型管理增强

- 新增模型供应商删除接口
- 前端供应商编辑页支持删除供应商
- 已启用模型支持删除操作
- 改进模型列表加载与供应商详情管理逻辑

### 7. 文档、配置与依赖更新

- README 增补项目历史、差异说明、Cookie 配置、环境变量说明等内容
- 新增超长视频处理方案文档、412 错误说明文档、GUI 启动器说明文档
- 补充 `FFMPEG_BIN_PATH` 等环境变量示例
- 前端引入并跟踪 `pnpm-lock.yaml`，并调整部分依赖与图标依赖
- 升级多项后端依赖与 Tauri 依赖，包含安全漏洞修复

## 二、相较 `48e7981de4254fbc4f7078a5bc08cf6c716936bd` 当前版本多出的功能

快照统计：

- 变更文件数：61
- 代码变更量：约 `20784` 行新增，`1129` 行删除

相较 `48e7981...`，当前版本比上面的内容还额外包含了 `e276afc...` 这一基线提交本身带来的能力增强。也就是说：

- `相较 48e7981` 的新增能力
  - 包含 `e276afc` 引入的 CUDA / 转写器健壮性增强
  - 也包含上一节列出的全部后续能力增强

其中可归纳为以下新增功能点：

### 1. CUDA 环境检查与转写器健壮性增强

- 新增 CUDA、Python、PyTorch、cuDNN 版本检查脚本：`check_cuda_pytorch_versions.py`
- 新增更完整的 CUDA 环境检查逻辑：自动补 PATH、检查 `cublas` / `cudnn` 相关库
- Whisper 转写器在 CUDA 不可用或 CUDA 库不兼容时，可自动回退到 CPU 模式
- 转写器在模型下载、加载、转写失败时提供更明确的错误日志

### 2. 从“能运行”提升到“更易用”

- 除原有核心能力外，当前版本已经新增本地启动脚本和 GUI 启动器
- 支持通过图形界面完成前后端启动、停止、端口检查、日志查看、系统诊断

### 3. 从“基础生成笔记”提升到“更稳定的长视频处理”

- 更适合超长视频、超长转录文本的总结流程
- 支持自动分块和失败降级，避免大请求直接打崩
- 支持缓存恢复与失败补偿，降低任务结果丢失的概率

### 4. 从“生成结果”提升到“结果可导出、可提醒、可恢复”

- 支持导出原文 Markdown
- 支持导出原文 SRT
- 支持浏览器通知
- 支持缺失结果文件的自动恢复

### 5. 从“可配置模型”提升到“可管理模型供应商”

- 支持删除模型供应商
- 支持删除已启用模型
- 支持更稳健的供应商连通性测试

## 三、结论

如果只看功能层面：

- 以 `e276afc...` 为基线到当前，主要是补齐了启动管理、B 站下载稳定性、长文本总结、任务恢复、导出与通知、供应商管理等能力
- 以 `48e7981...` 为基线到当前，除了以上全部内容，还额外包含了 CUDA 环境检查增强与 Whisper 转写器错误处理增强

如果你后面还希望我继续补一版更“发布说明风格”的 changelog，我可以再把这份内容改成：

- 按 `feat / fix / docs / build` 分组
- 按“用户可感知变化 / 内部技术变更”分组
- 或者直接整理成适合发到 GitHub Release 的版本说明

> GitHub Release 风格版本已单独输出到 [release.md](release.md)

---

## 四、按提交列表逐条展开的详细变更说明

> 以下为 `e276afc..HEAD` 区间内全部 60 个非合并提交的逐条说明，按时间顺序排列。
> 另有 1 个 `e276afc` 本身提交（相较 `48e7981` 独有的）在末尾单独列出。

### #1 `48e7981` — build(deps): bump h11 from 0.14.0 to 0.16.0

- **日期**: 2025-08-29
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级后端 HTTP 解析库 h11 至 0.16.0，修复潜在的安全问题
- **涉及目录**: `backend/`

### #2 `81775b3` — build(deps): bump slab

- **日期**: 2025-08-29
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 Tauri 前端 Rust 依赖 slab crate
- **涉及目录**: `BillNote_frontend/src-tauri/`

### #3 `1d776f2` — feat: 添加 CUDA 注意事项文档

- **日期**: 2025-08-29
- **作者**: YZz-S
- **类型**: feat / 文档
- **说明**: 新增 CUDA 注意事项文档，说明 Python、CUDA、cuDNN 和 PyTorch 版本对应关系
- **新增文件**: CUDA 环境配置说明文档

### #4 `ba49b4c` — fix: 更新 CUDA 注意事项文档

- **日期**: 2025-08-29
- **作者**: YZz-S
- **类型**: fix / 文档
- **说明**: 明确 GPU 型号和环境变量目标，修正文档细节

### #5 `acff319` — feat: 添加 CUDA 环境配置说明文档及版本检查脚本

- **日期**: 2025-08-29
- **作者**: YZz-S
- **类型**: feat / 工具
- **说明**: 新增 `check_cuda_pytorch_versions.py` 脚本，可自动检查 CUDA、Python、PyTorch、cuDNN 版本兼容性
- **新增文件**: `check_cuda_pytorch_versions.py`、环境配置说明文档

### #6 `62cacb9` — feat: 添加启动脚本

- **日期**: 2025-08-30
- **作者**: YZz-S
- **类型**: feat / 运维
- **说明**: 新增 `start_all.bat`、`start_all.ps1`、`start_all.sh`、`start_bilinote.bat`，支持一键启动后端和前端开发服务器
- **新增文件**: 4 个启动脚本

### #7 `84753cb` — feat: 添加封面保存到静态目录的功能

- **日期**: 2025-08-30
- **作者**: YZz-S
- **类型**: feat / 后端
- **说明**: 视频封面图保存到静态目录便于前端直接展示，优化截图生成逻辑
- **涉及文件**: 后端封面处理相关模块

### #8 `6f99fad` — fix: 优化 MarkdownViewer 图片路径处理

- **日期**: 2025-08-30
- **作者**: YZz-S
- **类型**: fix / 前端
- **说明**: 修复 `MarkdownViewer` 组件中图片相对路径拼接 baseURL 的问题，确保图片正确显示
- **涉及文件**: `BillNote_frontend/src/components/MarkdownViewer`

### #9 `1ffe706` — feat: 添加 conda 虚拟环境支持

- **日期**: 2025-09-06
- **作者**: YZz-S
- **类型**: feat / 运维
- **说明**: 启动脚本增加 conda 虚拟环境自动激活支持，降低环境配置门槛
- **涉及文件**: 启动脚本 (`start_all.ps1` 等)

### #10 `4e993a8` — chore: 更新 .gitignore

- **日期**: 2025-09-06
- **作者**: YZz-S
- **类型**: chore / 配置
- **说明**: 排除 ffmpeg 二进制文件和输出结果目录，保持仓库整洁
- **涉及文件**: `.gitignore`

### #11 `dfe16a1` — docs: 更新 README 文档

- **日期**: 2025-09-06
- **作者**: YZz-S
- **类型**: docs
- **说明**: 添加项目历史记录和差异说明，补充项目背景信息
- **涉及文件**: `README.md`

### #12 `b42b55e` — Update README.md

- **日期**: 2025-09-08
- **作者**: YZz-S
- **类型**: docs
- **说明**: README 文档内容补充更新
- **涉及文件**: `README.md`

### #13 `0be27ba` — feat: 添加提示词模板管理和 GUI 可视化功能说明

- **日期**: 2025-09-10
- **作者**: YZz-S
- **类型**: feat / 文档
- **说明**: 新增提示词模板管理功能说明和 GUI 启动器可视化功能文档
- **新增文件**: 相关功能说明文档

### #14 `996624e` — build(deps): bump starlette from 0.46.1 to 0.49.1

- **日期**: 2025-10-28
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 Starlette Web 框架至 0.49.1
- **涉及目录**: `backend/`

### #15 `90b6e19` — fix(backend): 增强 GPT 输入长度限制和错误处理

- **日期**: 2025-11-08
- **作者**: YZz-S
- **类型**: fix / 后端
- **说明**: 为 GPT 模型输入增加长度限制，超出时进行截断或降级处理，避免直接报错
- **涉及文件**: `backend/app/gpt/universal_gpt.py`

### #16 `7bdb228` — fix: 添加 cookiefile 配置以支持登录状态

- **日期**: 2025-11-08
- **作者**: YZz-S
- **类型**: fix / 后端
- **说明**: Bilibili 下载器支持通过 `cookiefile` 配置 Netscape 格式 Cookie 文件，降低登录态丢失导致的下载失败率
- **涉及文件**: `backend/app/downloaders/bilibili_downloader.py`

### #17 `0f81c45` — feat: 添加 BiliNote GUI 启动器核心模块

- **日期**: 2025-11-08
- **作者**: YZz-S
- **类型**: feat / 新功能
- **说明**: 新增 GUI 启动器核心实现：`gui_launcher.py`、`start_gui.py`、`modules/` 目录，支持图形化启动前后端、进程管理、端口检查、日志监控
- **新增文件**: `gui_launcher.py`、`start_gui.py`、`modules/`、`GUI_LAUNCHER_README.md`、PRD 和架构文档

### #18 `b7cdaab` — feat(bilibili): 添加 HTTP 请求头并优化 cookie 处理

- **日期**: 2025-11-23
- **作者**: YZz-S
- **类型**: feat / 后端
- **说明**: Bilibili 下载器补充更完整的 B 站 HTTP 请求头，优化 Cookie 读取和应用逻辑
- **涉及文件**: `backend/app/downloaders/bilibili_downloader.py`

### #19 `c30389a` — build(deps): bump fonttools from 4.58.4 to 4.61.0

- **日期**: 2025-12-01
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级字体处理库 fonttools
- **涉及目录**: `backend/`

### #20 `e7eb225` — build(deps): bump urllib3 from 2.3.0 to 2.6.3

- **日期**: 2026-01-08
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 HTTP 客户端库 urllib3，修复安全漏洞
- **涉及目录**: `backend/`

### #21 `befdd7d` — fix: 修复文件上传超时和内存问题

- **日期**: 2026-01-13
- **作者**: YZz-S
- **类型**: fix / 后端
- **说明**: 修复文件上传场景下的超时处理和内存占用问题
- **涉及文件**: 后端文件上传处理模块

### #22 `ca5d2cf` — feat(gpt): 添加长文本分段处理功能

- **日期**: 2026-01-13
- **作者**: YZz-S
- **类型**: feat / 后端
- **说明**: GPT 总结从简单截断升级为超长文本自动分段处理，遇到 `413 Request Entity Too Large` 时自动降级为分块重试
- **涉及文件**: `backend/app/gpt/universal_gpt.py`

### #23 `c3b108f` — build(deps): bump filelock from 3.18.0 to 3.20.3

- **日期**: 2026-01-13
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级文件锁库 filelock
- **涉及目录**: `backend/`

### #24 `be50dc1` — fix(video_reader): 改进视频帧提取的健壮性

- **日期**: 2026-01-17
- **作者**: YZz-S
- **类型**: fix / 后端
- **说明**: 改进视频帧提取的错误处理，增强对异常视频文件的兼容性
- **涉及文件**: 后端视频读取模块

### #25 `dba86cf` — feat(通知): 添加浏览器通知功能

- **日期**: 2026-01-17
- **作者**: YZz-S
- **类型**: feat / 前端
- **说明**: 新增浏览器通知能力，任务成功时调用 `notifyTaskSuccess`，失败时调用 `notifyTaskFailed`，主动提醒用户
- **新增文件**: `BillNote_frontend/src/utils/notification.ts`

### #26 `af849c2` — build(deps): bump weasyprint from 65.1 to 68.0

- **日期**: 2026-01-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 HTML 转 PDF 库 weasyprint
- **涉及目录**: `backend/`

### #27 `d701035` — build(deps): bump bytes

- **日期**: 2026-02-03
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 Tauri 前端 Rust 依赖 bytes crate
- **涉及目录**: `BillNote_frontend/src-tauri/`

### #28 `1f4b201` — build(deps): bump protobuf from 6.30.2 to 6.33.5

- **日期**: 2026-02-05
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 Protocol Buffers 库
- **涉及目录**: `backend/`

### #29 `2502a85` — build(deps): bump time

- **日期**: 2026-02-05
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 Tauri 前端 Rust 依赖 time crate
- **涉及目录**: `BillNote_frontend/src-tauri/`

### #30 `175997d` — build(deps): bump yt-dlp from 2025.3.31 to 2026.2.21

- **日期**: 2026-02-24
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级视频下载工具 yt-dlp 至 2026.2.21
- **涉及目录**: `backend/`

### #31 `317660d` — feat(导出): 添加原文转录的导出功能

- **日期**: 2026-02-25
- **作者**: YZz-S
- **类型**: feat / 前端
- **说明**: 新增 `buildSrtFromTranscript` 和 `buildMarkdownFromTranscript` 工具函数，支持将原始转录导出为 SRT 字幕和 Markdown 文件
- **新增文件**: `BillNote_frontend/src/utils/exporters.ts`

### #32 `0284683` — feat(HomePage): 为 MarkdownHeader 添加下载功能

- **日期**: 2026-02-25
- **作者**: YZz-S
- **类型**: feat / 前端
- **说明**: 在 `MarkdownHeader` 组件中新增"导出原文 .md"和"导出原文 .srt"操作按钮
- **涉及文件**: `BillNote_frontend/src/pages/HomePage/components/MarkdownHeader.tsx`

### #33 `c964e33` — docs: 添加超长视频转录摘要方案文档

- **日期**: 2026-02-25
- **作者**: YZz-S
- **类型**: docs
- **说明**: 新增处理超长视频转录摘要的方案说明文档，指导用户应对大视频场景
- **新增文件**: 超长视频处理方案文档

### #34 `f5622d4` — feat(bilibili_downloader): 从 CookieConfigManager 获取 Cookie

- **日期**: 2026-03-03
- **作者**: YZz-S
- **类型**: feat / 后端
- **说明**: Bilibili 下载器改为从 `CookieConfigManager` 统一获取并应用 B 站 Cookie，Cookie 管理更规范
- **涉及文件**: `backend/app/downloaders/bilibili_downloader.py`

### #35 `dfc862f` — docs: 添加 412 错误操作说明文档

- **日期**: 2026-03-03
- **作者**: YZz-S
- **类型**: docs
- **说明**: 针对 B 站常见的 HTTP 412 反爬错误，补充操作说明和解决方案文档
- **新增文件**: 412 错误说明文档

### #36 `18068b9` — chore: 更新开发环境配置和启动脚本

- **日期**: 2026-03-03
- **作者**: YZz-S
- **类型**: chore / 配置
- **说明**: 同步更新开发环境相关配置和启动脚本

### #37 `92408db` — fix(bilibili): 增强下载器反爬能力并修复短链解析

- **日期**: 2026-03-03
- **作者**: YZz-S
- **类型**: fix / 后端
- **说明**: 针对 `b23.tv` 短链增加真实地址自动解析，补充更完善的请求头和反爬策略
- **涉及文件**: `backend/app/downloaders/bilibili_downloader.py`

### #38 `af8db06` — fix: 后端端口从 8483 更改为 8492

- **日期**: 2026-03-03
- **作者**: YZz-S
- **类型**: fix / 配置
- **说明**: 临时更改后端服务端口为 8492（后在 #41 改回 8483）
- **涉及文件**: 后端配置文件

### #39 `452052b` — chore: 后端端口从 8483 改为 8492

- **日期**: 2026-03-03
- **作者**: YZz-S
- **类型**: chore / 配置
- **说明**: 配合 #38，同步更新相关配置中的端口值

### #40 `7991886` — fix: 修复端口配置不一致问题

- **日期**: 2026-03-03
- **作者**: YZz-S
- **类型**: fix / 配置
- **说明**: 修复多处端口配置不一致的问题，改进环境变量读取逻辑
- **涉及文件**: 前后端配置文件

### #41 `33aa741` — chore: 后端默认端口改回 8483

- **日期**: 2026-04-18
- **作者**: YZz-S
- **类型**: chore / 配置
- **说明**: 将后端默认端口从 8492 改回 8483，统一端口配置

### #42 `429a2f4` — docs(backend): 添加 FFMPEG_BIN_PATH 环境变量示例

- **日期**: 2026-04-18
- **作者**: YZz-S
- **类型**: docs
- **说明**: 在后端文档中补充 `FFMPEG_BIN_PATH` 环境变量的使用示例
- **涉及文件**: 后端配置文档

### #43 `51369fd` — build: 更新前端依赖并添加 pnpm 覆盖配置

- **日期**: 2026-04-18
- **作者**: YZz-S
- **类型**: build / 前端
- **说明**: 更新前端依赖包版本，添加 pnpm `overrides` 配置以统一依赖版本
- **涉及文件**: `package.json`、`pnpm-lock.yaml`

### #44 `46b4f46` — fix(frontend): track pnpm lockfile and align icon deps

- **日期**: 2026-04-18
- **作者**: YZz-S
- **类型**: fix / 前端
- **说明**: 将 `pnpm-lock.yaml` 纳入版本控制，对齐图标相关依赖版本
- **涉及文件**: `pnpm-lock.yaml`、前端依赖配置

### #45 `afe3ea3` — chore: 更新前端依赖并移除图片缩放功能

- **日期**: 2026-04-20
- **作者**: YZz-S
- **类型**: chore / 前端
- **说明**: 更新前端其他依赖项，移除不再需要的图片缩放功能
- **涉及文件**: 前端相关组件和配置

### #46 `0bca1e3` — build(deps): bump tornado from 6.4.2 to 6.5.5

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 Tornado Web 框架至 6.5.5，修复安全漏洞
- **涉及目录**: `backend/`

### #47 `52a1e22` — build(deps): bump pillow from 11.0.0 to 12.2.0

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级图像处理库 Pillow 至 12.2.0
- **涉及目录**: `backend/`

### #48 `7499a02` — build(deps): bump python-multipart from 0.0.20 to 0.0.26

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 multipart 表单解析库
- **涉及目录**: `backend/`

### #49 `7c2b9ed` — build(deps): bump aiohttp from 3.11.16 to 3.13.4

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级异步 HTTP 客户端 aiohttp 至 3.13.4
- **涉及目录**: `backend/`

### #50 `a8daa78` — build(deps): bump orjson from 3.10.16 to 3.11.6

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级高性能 JSON 库 orjson
- **涉及目录**: `backend/`

### #51 `f4fc0db` — build(deps): bump requests from 2.32.3 to 2.33.0

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 HTTP 库 requests
- **涉及目录**: `backend/`

### #52 `f8ec634` — build(deps): bump markdown from 3.8 to 3.8.1

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 Markdown 解析库
- **涉及目录**: `backend/`

### #53 `76486c5` — build(deps): bump pygments from 2.19.1 to 2.20.0

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级代码高亮库 Pygments
- **涉及目录**: `backend/`

### #54 `eb8e692` — build(deps): bump brotli from 1.1.0 to 1.2.0

- **日期**: 2026-04-20
- **作者**: dependabot[bot]
- **类型**: build / 依赖升级
- **说明**: 升级 Brotli 压缩库
- **涉及目录**: `backend/`

### #55 `d426a78` — build: 更新 Tauri 核心及插件依赖版本

- **日期**: 2026-04-20
- **作者**: YZz-S
- **类型**: build / 前端
- **说明**: 更新 Tauri 核心框架和各插件的 Rust 依赖版本
- **涉及文件**: `BillNote_frontend/src-tauri/Cargo.toml`、`Cargo.lock`

### #56 `6624b1d` — fix: 升级依赖以修复安全漏洞

- **日期**: 2026-04-20
- **作者**: YZz-S
- **类型**: fix / 安全
- **说明**: 批量升级存在已知安全漏洞的依赖项
- **涉及文件**: 前后端依赖配置文件

### #57 `b3ace13` — feat(task): 完善任务状态定义与轮询逻辑

- **日期**: 2026-05-29
- **作者**: YZz-S
- **类型**: feat / 前后端
- **说明**: 完善任务状态枚举定义，优化前端轮询逻辑，任务成功但结果不完整时增加兜底处理，优化错误分支的状态更新
- **涉及文件**: `BillNote_frontend/src/hooks/useTaskPolling.ts`、任务状态相关模块

### #58 `96bc500` — feat: 新增模型供应商删除功能

- **日期**: 2026-05-29
- **作者**: YZz-S
- **类型**: feat / 全栈
- **说明**: 后端新增 `delete_model_by_id` 方法和 `delete_provider` 接口；前端 `providerStore` 新增 `deleteProvider` 方法，`Form` 组件支持供应商删除操作
- **涉及文件**: `backend/app/services/model.py`、`backend/app/routers/provider.py`、`BillNote_frontend/src/store/providerStore/index.ts`、`BillNote_frontend/src/components/Form/modelForm/Form.tsx`

### #59 `7e910c1` — feat(backend): 完善连通性测试与长文本处理逻辑

- **日期**: 2026-05-29
- **作者**: YZz-S
- **类型**: feat / 后端
- **说明**: 优化连通性测试逻辑使其结合已保存模型做候选检查，完善长文本分段处理流程，优化异常捕获与提示
- **涉及文件**: `backend/app/gpt/universal_gpt.py`、`backend/app/services/note.py`

### #60 `bd8f2fd` — fix(backend,frontend): 完善笔记任务错误处理与缓存恢复逻辑

- **日期**: 2026-05-29
- **作者**: YZz-S
- **类型**: fix / 全栈
- **说明**: 后端新增 `build_note_result_from_cache` 缓存恢复函数，当结果文件缺失时自动从缓存恢复；结果为空或保存失败时主动标记任务失败并记录原因；前端轮询增加对成功但结果不完整场景的兜底处理；新增任务状态流转与缓存恢复测试用例
- **涉及文件**: `backend/app/routers/note.py`、`backend/app/services/note.py`、`BillNote_frontend/src/hooks/useTaskPolling.ts`、`backend/tests/test_task_status_flow.py`

---

### 附：相较 `48e7981` 独有的提交（`e276afc` 本身）

#### `e276afc` — feat: 增强转写器的错误处理和 CUDA 环境检查功能

- **日期**: 2025-08-29
- **作者**: YZz-S
- **类型**: feat / 后端
- **说明**: 这是 `48e7981` 和 `e276afc` 的共同父提交 `df72fa9` 之下的一个分支提交，相较 `48e7981` 多引入了以下能力：
  - `backend/app/utils/env_checker.py`: 大幅增强 CUDA 环境检查逻辑（+164 行），自动补 PATH、检查 `cublas` / `cudnn` 相关库
  - `backend/app/transcriber/whisper.py`: Whisper 转写器增加 CUDA 不可用或 CUDA 库不兼容时自动回退 CPU 模式（+110/-25 行）
  - `backend/app/services/note.py`: 笔记服务增加 CUDA 环境检查入口（+10 行）
  - `backend/requirements.txt`: 依赖版本微调
- **统计**: 4 files changed, 261 insertions(+), 25 deletions(-)
