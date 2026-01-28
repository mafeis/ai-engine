"""
AI 游戏引擎 - 后端服务主入口

功能模块:
- 项目管理: 创建/列表/删除游戏项目
- AI文档生成: 游戏设计文档自动扩写
- 资源生成: 图片/音频资源创建
- 游戏预览控制: 启动/停止游戏实例
"""

# Triggering reload to pick up configuration changes
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
import asyncio

# Windows 平台特殊配置：使用 ProactorEventLoop 以支持子进程
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from app.api import projects, documents, resources, game_control
from app.services.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时: 确保项目目录存在
    os.makedirs(settings.PROJECTS_DIR, exist_ok=True)
    print(f"✓ 项目目录已就绪: {settings.PROJECTS_DIR}")
    
    yield
    
    # 关闭时: 清理资源
    print("✓ 服务已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI 游戏引擎",
    description="基于 Phaser 3 的 AI 驱动游戏开发平台",
    version="0.1.0",
    lifespan=lifespan
)

# 配置 CORS (允许前端跨域访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(documents.router, prefix="/api/documents", tags=["文档生成"])
app.include_router(resources.router, prefix="/api/resources", tags=["资源生成"])
app.include_router(game_control.router, prefix="/api/game", tags=["游戏控制"])

# 静态文件服务 - 提供资源文件访问
app.mount("/assets", StaticFiles(directory=settings.PROJECTS_DIR), name="assets")


@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "service": "AI 游戏引擎",
        "status": "运行中",
        "version": "0.1.0"
    }


@app.get("/api/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "projects_dir": settings.PROJECTS_DIR,
        "llm_configured": bool(settings.LLM_BASE_URL)
    }
