"""
项目管理 API

提供游戏项目的 CRUD 操作
- 创建新游戏项目
- 获取项目列表
- 获取项目详情
- 删除项目
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import json
import shutil
import uuid

from app.services.config import settings

router = APIRouter()


# ============ 数据模型 ============

class ProjectCreate(BaseModel):
    """创建项目请求"""
    name: str                    # 游戏名称
    intro: str                   # 游戏简介
    game_type: Optional[str] = "2D横版"  # 游戏类型
    art_style: Optional[str] = "像素风"  # 美术风格


class ProjectInfo(BaseModel):
    """项目信息"""
    id: str
    name: str
    intro: str
    game_type: str
    art_style: str
    created_at: str
    status: str  # draft / designing / resources / ready / published


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    projects: List[ProjectInfo]
    total: int


# ============ API 端点 ============

@router.post("/", response_model=ProjectInfo)
async def create_project(project: ProjectCreate):
    """
    创建新的游戏项目
    
    流程:
    1. 生成项目ID
    2. 创建项目目录结构
    3. 保存项目元数据
    """
    # 生成唯一项目ID
    project_id = str(uuid.uuid4())[:8]
    project_dir = os.path.join(settings.PROJECTS_DIR, project_id)
    
    try:
        # 创建项目目录结构
        os.makedirs(project_dir, exist_ok=True)
        for subdir in ["documents", "specs", "scripts/generators", 
                       "assets/characters", "assets/scenes", "assets/items",
                       "assets/ui", "assets/audio/bgm", "assets/audio/sfx",
                       "configs", "game/src"]:
            os.makedirs(os.path.join(project_dir, subdir), exist_ok=True)
        
        # 创建项目元数据
        metadata = {
            "id": project_id,
            "name": project.name,
            "intro": project.intro,
            "game_type": project.game_type,
            "art_style": project.art_style,
            "created_at": datetime.now().isoformat(),
            "status": "draft"
        }
        
        # 保存元数据
        metadata_path = os.path.join(project_dir, "project.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return ProjectInfo(**metadata)
        
    except Exception as e:
        # 清理失败的项目目录
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")


@router.get("/", response_model=ProjectListResponse)
async def list_projects():
    """获取所有项目列表"""
    projects = []
    projects_dir = settings.PROJECTS_DIR
    
    if not os.path.exists(projects_dir):
        return ProjectListResponse(projects=[], total=0)
    
    for project_id in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_id)
        metadata_path = os.path.join(project_path, "project.json")
        
        if os.path.isdir(project_path) and os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    projects.append(ProjectInfo(**metadata))
            except Exception:
                pass  # 跳过无效项目
    
    # 按创建时间排序（最新优先）
    projects.sort(key=lambda x: x.created_at, reverse=True)
    
    return ProjectListResponse(projects=projects, total=len(projects))


@router.get("/{project_id}", response_model=ProjectInfo)
async def get_project(project_id: str):
    """获取项目详情"""
    metadata_path = os.path.join(settings.PROJECTS_DIR, project_id, "project.json")
    
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="项目不存在")
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    return ProjectInfo(**metadata)


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    project_path = os.path.join(settings.PROJECTS_DIR, project_id)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="项目不存在")
    
    try:
        shutil.rmtree(project_path)
        return {"message": "项目已删除", "project_id": project_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.patch("/{project_id}/status")
async def update_project_status(project_id: str, status: str):
    """更新项目状态"""
    metadata_path = os.path.join(settings.PROJECTS_DIR, project_id, "project.json")
    
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="项目不存在")
    
    valid_statuses = ["draft", "designing", "resources", "ready", "published"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效状态，可选: {valid_statuses}")
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    metadata["status"] = status
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return {"message": "状态已更新", "status": status}
