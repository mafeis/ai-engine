# AI 游戏引擎 (AI Engine)

基于 Phaser 3 的 AI 驱动游戏开发平台。通过自然语言描述自动生成游戏设计文档、资源（图片/音频）并实时预览。

## 🚀 项目简介

AI 游戏引擎是一个集成的开发环境，旨在通过生成式 AI 简化游戏原型设计。用户只需输入简单的创意描述，系统即可自动扩展为详细的设计文档，并生成配套的游戏资产。

## ✨ 核心特性

- 📝 **AI 驱动的文档生成**: 自动扩写游戏背景、角色设定、关卡设计等。
- 🎨 **资产自动化**: 基于描述生成符合风格的图片和占位符资源。
- 🕹️ **实时预览**: 集成 Phaser 3 引擎，支持游戏实例的即时启动与停止。
- 🌿 **多版本管理**: 支持资源的不同版本选择与迭代。
- 🛠️ **项目管理**: 便捷地创建、列表和删除本地游戏项目。

## 🛠️ 技术栈

### 后端 (Backend)
- **框架**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI 交互**: 本地部署的 LLM (如 Ollama Qwen 2.5)
- **工具**: Pydantic, Uvicorn

### 前端 (Frontend)
- **框架**: [Vite](https://vitejs.dev/) + Vanilla JavaScript
- **渲染引擎**: [Phaser 3](https://phaser.io/)
- **样式**: CSS3

## 📂 项目结构

```text
ai-engine/
├── backend/            # FastAPI 后端服务
│   ├── app/            # 应用逻辑代码
│   │   ├── api/        # 接口路由
│   │   ├── services/   # 业务逻辑
│   │   └── models/     # 数据模型
│   └── scripts/        # 辅助脚本
├── frontend/           # 前端编辑器界面
│   ├── src/            # 前端源码
│   └── index.html      # 主入口
├── game-template/      # 标准化 Phaser 游戏模板
├── projects/           # 用户生成游戏项目存储 (目前被 .gitignore 忽略)
├── shared/             # 跨模块共享配置与模式
└── .gitignore          # Git 忽略配置
```

## ⚙️ 快速开始

### 1. 后端配置
```bash
cd backend
pip install -r requirements.txt
# 确保已配置 .env 文件
python -m uvicorn app.main:app --reload
```

### 2. 前端配置
```bash
cd frontend
npm install
npm run dev
```

## ❓ 常见问题

### 为什么生成的项目 (projects/) 没有在 Git 提交中显示？

这是因为根目录的 `.gitignore` 文件中包含以下内容：
```text
projects/
shared/
```
这会导致 Git 忽略这些文件夹下的所有更改。如果你希望将生成的项目或共享代码提交到仓库，需要从 `.gitignore` 中移除它们。
