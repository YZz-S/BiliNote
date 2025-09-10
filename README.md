<div style="display: flex; justify-content: center; align-items: center; gap: 10px;
">
    <p align="center">
  <img src="./doc/icon.svg" alt="BiliNote Banner" width="50" height="50"  />
</p>
<h1 align="center" > BiliNote v1.8.1</h1>
</div>

<p align="center"><i>AI 视频笔记生成工具 让 AI 为你的视频做笔记</i></p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" />
  <img src="https://img.shields.io/badge/frontend-react-blue" />
  <img src="https://img.shields.io/badge/backend-fastapi-green" />
  <img src="https://img.shields.io/badge/GPT-openai%20%7C%20deepseek%20%7C%20qwen-ff69b4" />
  <img src="https://img.shields.io/badge/docker-compose-blue" />
  <img src="https://img.shields.io/badge/status-active-success" />
  <img src="https://img.shields.io/github/stars/jefferyhcool/BiliNote?style=social" />
</p>



## ✨ 项目简介

BiliNote 是一个开源的 AI 视频笔记助手，支持通过哔哩哔哩、YouTube、抖音等视频链接，自动提取内容并生成结构清晰、重点明确的 Markdown 格式笔记。支持插入截图、原片跳转等功能。

## 📈 历史提交记录总结

### 主要开发里程碑
本项目基于原版BiliNote进行开发，以下是YZz-S在my_dev提交范围 `e276afcb7e4817b2519d2d47ae3c91ed71accc16` 到 `62cacb9d7dd6755df71534dc4235091f631ccfab` 之间的主要开发记录：

#### 使用便利性
添加启动脚本以启动BiliNote开发环境，包括后端和前端服务器

#### CUDA  环境配置
添加CUDA、Python、PyTorch和cuDNN环境配置说明文档及版本检查脚本
增强转写器的错误处理和CUDA环境检查功能

## 🚀 更新计划

### 近期开发计划

#### 批量总结功能开发
- **批量视频处理**：支持一次性导入多个视频链接进行批量处理
- **批量笔记生成**：实现多视频内容的统一总结和归纳
- **进度管理**：提供批量任务的进度跟踪和状态管理
- **结果导出**：支持批量笔记的统一导出和格式化

#### 收藏夹文件夹自动总结功能
- **收藏夹导入**：支持从各平台导入收藏夹或播放列表
- **智能分类**：根据视频内容自动进行主题分类
- **文件夹总结**：为每个分类生成综合性总结报告
- **知识图谱**：构建视频内容之间的关联关系

#### 提示词模板

- **提示词管理**：支持创建、更新、删除提示词模板
- **提示词快捷使用**：在生成笔记页面快捷选择提示词模板

#### 启动GUI

- **可视化管理**：支持通过GUI一键开启、结束前后端进程
- **可视化监控**：支持通过GUI查看后端进程和log

### 中长期规划

#### 大语言模型
集成多种大语言模型（Kimi、豆包等）进行智能笔记生成

#### 功能扩展
- **多语言支持**：扩展对更多语言的音频转写和笔记生成支持
- **实时处理**：支持直播流的实时笔记生成
- **协作功能**：添加多用户协作和笔记分享功能
- **移动端适配**：开发移动端应用或响应式设计


## 🔄 项目差异说明

本项目基于原版 [BiliNote](https://github.com/JefferyHcool/BiliNote) 进行开发，以下是主要差异：

### 功能差异
- **保持核心功能一致**：继承了原版的所有核心功能，包括多平台视频支持、AI笔记生成、截图插入等
- **功能扩展**：在原版基础上可能进行了功能优化和扩展（具体差异请参考代码变更记录）
- **用户体验优化**：可能对界面交互和用户流程进行了改进

### 技术实现差异
- **架构保持**：延续原版的 FastAPI + React + Vite 技术栈
- **依赖管理**：可能更新了部分依赖包版本以提升安全性和性能
- **代码优化**：可能对部分代码逻辑进行了重构和优化
- **配置调整**：可能对环境配置和部署方式进行了微调

### 部署差异
- **Docker支持**：继承原版的Docker部署方案
- **环境配置**：保持与原版兼容的环境变量配置
- **依赖要求**：FFmpeg、CUDA等依赖要求与原版保持一致

### 其他差异
- **文档更新**：可能对文档内容进行了补充和完善
- **许可协议**：严格遵循原版的MIT许可协议
- **社区支持**：建议优先参考原版项目的官方文档和社区支持

> **注意**：本项目旨在学习和研究目的，建议用户优先使用原版项目以获得最佳体验和官方支持。

## 📋 版权声明与知识产权

### 原项目信息
本项目基于以下开源项目进行开发：
- **原项目名称**：BiliNote
- **原项目地址**：https://github.com/JefferyHcool/BiliNote
- **原作者**：JefferyHcool
- **原项目许可**：MIT License

### 版权归属
- **原创代码版权**：归属于原作者 JefferyHcool
- **修改部分版权**：本项目的修改和扩展部分遵循原项目的MIT许可协议
- **第三方依赖**：项目中使用的第三方库和组件版权归其各自作者所有

### 开源协议遵循
- 本项目严格遵循原项目的 **MIT License** 许可协议
- 保留原项目的版权声明和许可条款
- 对原项目的任何修改都将在相同许可协议下发布
- 使用本项目时请同时遵守原项目和本项目的许可条款

### 引用内容来源
本项目引用的外部资源和代码片段均已在相应位置标注来源：
- 抖音下载功能：[Evil0ctal/Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API)
- Fast-Whisper：[SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- 其他第三方库：详见 `package.json` 和 `requirements.txt`

### 知识产权声明
- **尊重原创**：本项目充分尊重原作者的知识产权和创作成果
- **学习目的**：本项目主要用于学习、研究和技术交流
- **商业使用**：如需商业使用，请确保遵循相关开源协议的要求
- **免责声明**：使用本项目产生的任何问题由使用者自行承担责任

### 致谢
感谢原作者 JefferyHcool 创建了如此优秀的开源项目，为AI视频笔记领域做出了重要贡献。本项目的存在是对原项目的学习和致敬。

## 📝 使用文档
详细文档可以查看[这里](https://docs.bilinote.app/)

## 体验地址
可以通过访问 [这里](https://www.bilinote.app/) 进行体验，速度略慢，不支持长视频。
## 📦 Windows 打包版
本项目提供了 Windows 系统的 exe 文件，可在[release](https://github.com/JefferyHcool/BiliNote/releases/tag/v1.1.1)进行下载。**注意一定要在没有中文路径的环境下运行。**


## 🔧 功能特性

- 支持多平台：Bilibili、YouTube、本地视频、抖音（后续会加入更多平台）
- 支持返回笔记格式选择
- 支持笔记风格选择
- 支持多模态视频理解
- 支持多版本记录保留
- 支持自行配置 GPT 大模型
- 本地模型音频转写（支持 Fast-Whisper）
- GPT 大模型总结视频内容
- 自动生成结构化 Markdown 笔记
- 可选插入截图（自动截取）
- 可选内容跳转链接（关联原视频）
- 任务记录与历史回看

## 📸 截图预览
![screenshot](./doc/image1.png)
![screenshot](./doc/image3.png)
![screenshot](./doc/image.png)
![screenshot](./doc/image4.png)
![screenshot](./doc/image5.png)

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/JefferyHcool/BiliNote.git
cd BiliNote
mv .env.example .env
```

### 2. 启动后端（FastAPI）

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 3. 启动前端（Vite + React）

```bash
cd BillNote_frontend
pnpm install
pnpm dev
```

访问：`http://localhost:5173`

## ⚙️ 依赖说明
### 🎬 FFmpeg
本项目依赖 ffmpeg 用于音频处理与转码，必须安装：
```bash
# Mac (brew)
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
# 请从官网下载安装：https://ffmpeg.org/download.html
```
> ⚠️ 若系统无法识别 ffmpeg，请将其加入系统环境变量 PATH

### 🚀 CUDA 加速（可选）
若你希望更快地执行音频转写任务，可使用具备 NVIDIA GPU 的机器，并启用 fast-whisper + CUDA 加速版本：

具体 `fast-whisper` 配置方法，请参考：[fast-whisper 项目地址](http://github.com/SYSTRAN/faster-whisper#requirements)

### 🐳 使用 Docker 一键部署

确保你已安装 Docker 和 Docker Compose：

[docker 部署](https://github.com/JefferyHcool/bilinote-deploy/blob/master/README.md)

## 🧠 TODO

- [x] 支持抖音及快手等视频平台
- [x] 支持前端设置切换 AI 模型切换、语音转文字模型
- [x] AI 摘要风格自定义（学术风、口语风、重点提取等）
- [ ] 笔记导出为 PDF / Word / Notion
- [x] 加入更多模型支持
- [x] 加入更多音频转文本模型支持

### Contact and Join-联系和加入社区
- BiliNote 交流QQ群：785367111
- BiliNote 交流微信群:
  
  <img src="doc/wechat.png" alt="wechat" style="zoom:33%;" />



## 🔎代码参考
- 本项目中的 `抖音下载功能` 部分代码参考引用自：[Evil0ctal/Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API)

## 📜 License

MIT License

---

💬 你的支持与反馈是我持续优化的动力！欢迎 PR、提 issue、Star ⭐️
## Buy Me a Coffee / 捐赠
如果你觉得项目对你有帮助，考虑支持我一下吧
<div style='display:inline;'>
    <img width='30%' src='https://common-1304618721.cos.ap-chengdu.myqcloud.com/8986c9eb29c356a0cfa3d470c23d3b6.jpg'/>
    <img width='30%' src='https://common-1304618721.cos.ap-chengdu.myqcloud.com/2a049ea298b206bcd0d8b8da3219d6b.jpg'/>
</div>

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JefferyHcool/BiliNote&type=Date)](https://www.star-history.com/#JefferyHcool/BiliNote&Date)
