"""
文档生成 API

提供 AI 驱动的游戏设计文档生成功能
- 生成主设计文档
- 生成细化模块文档（角色/玩法/场景等）
- 提取 JSON 规格
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json

from app.services.config import settings
from app.services.llm_service import LLMService

router = APIRouter()
llm = LLMService()


# ============ 数据模型 ============

class GenerateDocRequest(BaseModel):
    """生成文档请求"""
    project_id: str
    doc_type: str = "main"  # main / character / gameplay / scene / item / quest / ui / audio


class ExtractSpecRequest(BaseModel):
    """提取JSON规格请求"""
    project_id: str
    doc_type: str  # character / gameplay / scene / item / quest / ui / audio


class DocumentResponse(BaseModel):
    """文档响应"""
    project_id: str
    doc_type: str
    content: str
    file_path: str


# ============ 文档类型配置 ============

DOC_TYPES = {
    "main": {
        "filename": "game_design.md",
        "title": "游戏设计文档"
    },
    "character": {
        "filename": "character_design.md",
        "title": "角色设计文档"
    },
    "gameplay": {
        "filename": "gameplay_design.md",
        "title": "玩法设计文档"
    },
    "scene": {
        "filename": "scene_design.md",
        "title": "场景设计文档"
    },
    "item": {
        "filename": "item_design.md",
        "title": "道具设计文档"
    },
    "quest": {
        "filename": "quest_design.md",
        "title": "任务设计文档"
    },
    "ui": {
        "filename": "ui_design.md",
        "title": "UI设计文档"
    },
    "audio": {
        "filename": "audio_design.md",
        "title": "音频设计文档"
    }
}


# ============ API 端点 ============

@router.get("/{project_id}/list")
async def list_documents(project_id: str):
    """
    获取项目的所有文档列表
    
    返回每个文档的类型、标题、是否存在
    """
    docs_dir = os.path.join(settings.PROJECTS_DIR, project_id, "documents")
    
    if not os.path.exists(docs_dir):
        raise HTTPException(status_code=404, detail="项目不存在")
    
    documents = []
    for doc_type, config in DOC_TYPES.items():
        doc_path = os.path.join(docs_dir, config["filename"])
        exists = os.path.exists(doc_path)
        
        doc_info = {
            "doc_type": doc_type,
            "title": config["title"],
            "filename": config["filename"],
            "exists": exists,
            "file_path": doc_path if exists else None
        }
        
        # 如果存在，获取文件大小和修改时间
        if exists:
            stat = os.stat(doc_path)
            doc_info["size"] = stat.st_size
            doc_info["modified_at"] = stat.st_mtime
        
        documents.append(doc_info)
    
    return {
        "project_id": project_id,
        "documents": documents,
        "total": len(documents),
        "generated": sum(1 for d in documents if d["exists"])
    }


@router.post("/generate", response_model=DocumentResponse)
async def generate_document(request: GenerateDocRequest):
    """
    生成设计文档
    
    根据项目信息和文档类型，调用 LLM 生成相应的设计文档
    """
    # 验证项目存在
    project_path = os.path.join(settings.PROJECTS_DIR, request.project_id)
    metadata_path = os.path.join(project_path, "project.json")
    
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 验证文档类型
    if request.doc_type not in DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的文档类型: {request.doc_type}")
    
    # 读取项目信息
    with open(metadata_path, "r", encoding="utf-8") as f:
        project = json.load(f)
    
    # 调用 LLM 生成文档
    doc_config = DOC_TYPES[request.doc_type]
    content = await llm.generate_document(
        project_name=project["name"],
        project_intro=project["intro"],
        game_type=project["game_type"],
        art_style=project["art_style"],
        doc_type=request.doc_type
    )
    
    # 保存文档
    doc_path = os.path.join(project_path, "documents", doc_config["filename"])
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return DocumentResponse(
        project_id=request.project_id,
        doc_type=request.doc_type,
        content=content,
        file_path=doc_path
    )


@router.get("/{project_id}/specs")
async def list_specs(project_id: str):
    """获取项目所有规格文件列表"""
    specs_dir = os.path.join(settings.PROJECTS_DIR, project_id, "specs")
    
    if not os.path.exists(specs_dir):
        return {"project_id": project_id, "specs": [], "total": 0, "extracted": 0}
    
    # 可提取规格的文档类型
    spec_types = ["character", "scene", "item", "audio", "gameplay", "quest", "ui"]
    
    specs = []
    for spec_type in spec_types:
        spec_path = os.path.join(specs_dir, f"{spec_type}.json")
        exists = os.path.exists(spec_path)
        
        spec_info = {
            "spec_type": spec_type,
            "title": DOC_TYPES.get(spec_type, {}).get("title", spec_type),
            "exists": exists
        }
        
        if exists:
            stat = os.stat(spec_path)
            spec_info["size"] = stat.st_size
            spec_info["modified_at"] = stat.st_mtime
            
            # 读取规格文件内容概要
            try:
                with open(spec_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 统计条目数量
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list):
                                spec_info["item_count"] = len(value)
                                break
            except Exception:
                pass
        
        specs.append(spec_info)
    
    return {
        "project_id": project_id,
        "specs": specs,
        "total": len(specs),
        "extracted": sum(1 for s in specs if s["exists"])
    }


@router.get("/{project_id}/{doc_type}")
async def get_document(project_id: str, doc_type: str):
    """获取已生成的文档"""
    if doc_type not in DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的文档类型: {doc_type}")
    
    doc_config = DOC_TYPES[doc_type]
    doc_path = os.path.join(
        settings.PROJECTS_DIR, project_id, "documents", doc_config["filename"]
    )
    
    if not os.path.exists(doc_path):
        raise HTTPException(status_code=404, detail="文档不存在")
    
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return DocumentResponse(
        project_id=project_id,
        doc_type=doc_type,
        content=content,
        file_path=doc_path
    )


@router.put("/{project_id}/{doc_type}")
async def update_document(project_id: str, doc_type: str, content: str):
    """更新文档内容（用户编辑后保存）"""
    if doc_type not in DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的文档类型: {doc_type}")
    
    doc_config = DOC_TYPES[doc_type]
    doc_path = os.path.join(
        settings.PROJECTS_DIR, project_id, "documents", doc_config["filename"]
    )
    
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return {"message": "文档已保存", "file_path": doc_path}


@router.post("/extract-spec")
async def extract_spec(request: ExtractSpecRequest):
    """
    从文档提取 JSON 规格
    
    将 Markdown 文档中的设计转换为结构化 JSON 数据
    """
    # 读取对应的文档
    doc_config = DOC_TYPES.get(request.doc_type)
    if not doc_config:
        raise HTTPException(status_code=400, detail=f"无效的文档类型: {request.doc_type}")
    
    doc_path = os.path.join(
        settings.PROJECTS_DIR, request.project_id, "documents", doc_config["filename"]
    )
    
    if not os.path.exists(doc_path):
        raise HTTPException(status_code=404, detail="请先生成对应的设计文档")
    
    with open(doc_path, "r", encoding="utf-8") as f:
        doc_content = f.read()
    
    # 调用 LLM 提取规格
    spec_data = await llm.extract_spec(doc_content, request.doc_type)
    
    # 保存规格文件
    spec_path = os.path.join(
        settings.PROJECTS_DIR, request.project_id, "specs", f"{request.doc_type}.json"
    )
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec_data, f, ensure_ascii=False, indent=2)
    
    return {
        "project_id": request.project_id,
        "doc_type": request.doc_type,
        "spec": spec_data,
        "file_path": spec_path
    }


@router.get("/{project_id}/specs/{spec_type}")
async def get_spec(project_id: str, spec_type: str):
    """获取 JSON 规格文件"""
    spec_path = os.path.join(
        settings.PROJECTS_DIR, project_id, "specs", f"{spec_type}.json"
    )
    
    if not os.path.exists(spec_path):
        raise HTTPException(status_code=404, detail="规格文件不存在")
    
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_data = json.load(f)
    
    return {
        "project_id": project_id,
        "spec_type": spec_type,
        "spec": spec_data
    }
