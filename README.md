# AI 游戏引擎

基于 Phaser 3 的 AI 驱动游戏开发平台。通过自然语言描述自动生成游戏设计文档和资源。

## 项目结构

```
ai-engine/
├── backend/          # Python 后端服务
├── frontend/         # Node.js 前端编辑器
├── game-template/    # Phaser 游戏模板
├── shared/           # 共享配置和模式
└── projects/         # 用户游戏项目存储
```

## 技术栈

- **后端**: Python + FastAPI
- **前端**: Node.js + Vite
- **游戏引擎**: Phaser 3
- **AI**: 本地部署 LLM

## 快速开始

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 功能

- [x] 项目基础结构
- [ ] 游戏设计文档 AI 生成
- [ ] 资源自动生成（图片/音频）
- [ ] 游戏预览控制（启动/停止）
- [ ] 多版本资源选择
