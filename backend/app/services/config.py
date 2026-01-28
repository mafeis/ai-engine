"""
应用配置管理

使用 pydantic-settings 从环境变量加载配置
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # AI 服务配置 (本地部署)
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_MODEL: str = "qwen2.5:14b"
    LLM_API_KEY: str = "ollama"
    
    # 服务端口
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000
    GAME_PREVIEW_PORT: int = 8080
    
    # 项目存储路径
    # 修改为相对于 workspace root 的路径，如果从 backend 目录运行，则是 ../projects
    PROJECTS_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../projects"))
    
    # 资源生成配置
    DEFAULT_IMAGE_SIZE: int = 64
    DEFAULT_AUDIO_SAMPLE_RATE: int = 44100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()
