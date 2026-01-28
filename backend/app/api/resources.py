"""
资源生成 API

提供图片和音频资源的 AI 生成功能
- 生成资源脚本
- 执行脚本创建资源
- 资源版本管理
- 资源选择与确认
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys
import asyncio

# Windows 平台特殊配置：使用 ProactorEventLoop 以支持子进程
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
import json
import subprocess
import uuid
from datetime import datetime

from app.services.config import settings
from app.services.llm_service import LLMService

router = APIRouter()
llm = LLMService()


# ============ 数据模型 ============

class GenerateResourceRequest(BaseModel):
    """生成资源请求"""
    project_id: str
    resource_type: str  # character / scene / item / ui / bgm / sfx
    resource_id: str    # 资源唯一标识 (如角色名)
    description: str    # 自然语言描述
    params: Optional[Dict[str, Any]] = None  # 生成参数


class ResourceParams(BaseModel):
    """资源生成参数"""
    # 图片参数
    size: Optional[int] = 64        # 尺寸 (16/32/64/128/256)
    style: Optional[str] = "pixel"  # 风格 (pixel/cartoon)
    colors: Optional[int] = 16      # 颜色数
    
    # 音频参数
    duration: Optional[float] = 2.0     # 时长（秒）
    sample_rate: Optional[int] = 44100  # 采样率


class ResourceVariant(BaseModel):
    """资源变体"""
    variant_id: str
    file_path: str
    created_at: str
    params: Dict[str, Any]
    selected: bool = False


# ============ 资源类型配置 ============

RESOURCE_TYPES = {
    "character": {"folder": "characters", "extension": ".png", "category": "image"},
    "scene": {"folder": "scenes", "extension": ".png", "category": "image"},
    "item": {"folder": "items", "extension": ".png", "category": "image"},
    "ui": {"folder": "ui", "extension": ".png", "category": "image"},
    "bgm": {"folder": "audio/bgm", "extension": ".wav", "category": "audio"},
    "sfx": {"folder": "audio/sfx", "extension": ".wav", "category": "audio"},
}


# ============ API 端点 ============

@router.post("/generate")
async def generate_resource(request: GenerateResourceRequest):
    """
    生成资源
    
    流程:
    1. 调用 LLM 生成 Python 脚本
    2. 执行脚本生成资源文件
    3. 保存到变体目录供选择
    """
    # 验证资源类型
    if request.resource_type not in RESOURCE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的资源类型: {request.resource_type}")
    
    resource_config = RESOURCE_TYPES[request.resource_type]
    project_path = os.path.join(settings.PROJECTS_DIR, request.project_id)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 准备参数
    params = request.params or {}
    params.setdefault("size", settings.DEFAULT_IMAGE_SIZE)
    params.setdefault("sample_rate", settings.DEFAULT_AUDIO_SAMPLE_RATE)
    
    # 生成变体ID
    variant_id = str(uuid.uuid4())[:8]
    
    # 资源目录路径
    resource_dir = os.path.join(
        project_path, "assets", resource_config["folder"], request.resource_id
    )
    variants_dir = os.path.join(resource_dir, "variants")
    os.makedirs(variants_dir, exist_ok=True)
    
    # 调用 LLM 生成脚本
    script_content = await llm.generate_resource_script(
        resource_type=request.resource_type,
        description=request.description,
        params=params,
        category=resource_config["category"]
    )
    
    # 保存脚本
    script_path = os.path.join(
        project_path, "scripts", "generators", 
        f"{request.resource_type}_{request.resource_id}_{variant_id}.py"
    )
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # 输出文件路径
    output_path = os.path.join(
        variants_dir, f"{variant_id}{resource_config['extension']}"
    )
    
    # 执行脚本生成资源
    import subprocess
    try:
        result = subprocess.run(
            ["python", script_path, "--output", output_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500, 
                detail=f"脚本执行失败: {result.stderr}"
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="脚本执行超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 保存变体元数据
    variant_meta = {
        "variant_id": variant_id,
        "file_path": output_path,
        "script_path": script_path,
        "created_at": datetime.now().isoformat(),
        "params": params,
        "description": request.description,
        "selected": False
    }
    
    meta_path = os.path.join(variants_dir, f"{variant_id}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(variant_meta, f, ensure_ascii=False, indent=2)
    
    return {
        "project_id": request.project_id,
        "resource_type": request.resource_type,
        "resource_id": request.resource_id,
        "variant": variant_meta
    }


@router.get("/{project_id}/{resource_type}/{resource_id}/variants")
async def list_variants(project_id: str, resource_type: str, resource_id: str):
    """获取资源的所有变体（从temp临时目录读取）"""
    if resource_type not in RESOURCE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的资源类型: {resource_type}")
    
    resource_config = RESOURCE_TYPES[resource_type]
    
    # 路径统一使用绝对路径
    projects_dir_abs = os.path.abspath(settings.PROJECTS_DIR)
    project_path = os.path.join(projects_dir_abs, project_id)
    
    # 从temp临时目录读取候选变体
    variants_dir = os.path.join(
        project_path, "temp",
        resource_config["folder"], resource_id, "variants"
    )
    
    if not os.path.exists(variants_dir):
        return {"variants": [], "total": 0}
    
    variants = []
    for filename in os.listdir(variants_dir):
        if filename.endswith(".json"):
            with open(os.path.join(variants_dir, filename), "r", encoding="utf-8") as f:
                variant_data = json.load(f)
                # 检查文件是否真实存在
                variant_data["exists"] = os.path.exists(variant_data.get("file_path", ""))
                variants.append(variant_data)
    
    # 按创建时间排序
    variants.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # 检查是否存在序列帧动画 (仅限角色)
    animation = None
    if resource_type == "character":
        anim_path = os.path.join(project_path, "assets", "characters", resource_id, "animations", "spritesheet.png")
        if os.path.exists(anim_path):
            animation = {
                "spritesheet_url": f"/assets/{project_id}/assets/characters/{resource_id}/animations/spritesheet.png",
                "exists": True
            }
    
    return {
        "variants": variants, 
        "total": len(variants),
        "animation": animation
    }


@router.post("/{project_id}/{resource_type}/{resource_id}/select/{variant_id}")
async def select_variant(
    project_id: str, resource_type: str, resource_id: str, variant_id: str
):
    """
    选择并确认一个变体作为最终资源
    
    从temp临时目录复制选中的资源到正式assets目录
    """
    if resource_type not in RESOURCE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的资源类型: {resource_type}")
    
    resource_config = RESOURCE_TYPES[resource_type]
    
    # 路径统一使用绝对路径
    projects_dir_abs = os.path.abspath(settings.PROJECTS_DIR)
    project_path = os.path.join(projects_dir_abs, project_id)
    
    # 临时目录（候选变体所在位置）
    temp_dir = os.path.join(project_path, "temp", resource_config["folder"], resource_id)
    temp_variants_dir = os.path.join(temp_dir, "variants")
    
    # 正式资源目录（最终资源存放位置）
    assets_dir = os.path.join(project_path, "assets", resource_config["folder"], resource_id)
    os.makedirs(assets_dir, exist_ok=True)
    
    # 查找变体元数据
    variant_meta_path = os.path.join(temp_variants_dir, f"{variant_id}.json")
    if not os.path.exists(variant_meta_path):
        raise HTTPException(status_code=404, detail="变体不存在")
    
    with open(variant_meta_path, "r", encoding="utf-8") as f:
        variant = json.load(f)
    
    # 源文件（temp目录中的候选）
    src_file = variant["file_path"]
    if not os.path.exists(src_file):
        raise HTTPException(status_code=404, detail="变体文件不存在")
    
    # 目标文件（正式assets目录）
    final_filename = f"{resource_id}{resource_config['extension']}"
    dst_file = os.path.join(assets_dir, final_filename)
    
    # 复制到正式目录
    import shutil
    shutil.copy2(src_file, dst_file)
    
    # 更新变体状态（在temp目录的元数据中标记已选择）
    # 先清除其他变体的selected状态
    for filename in os.listdir(temp_variants_dir):
        if filename.endswith(".json"):
            meta_path = os.path.join(temp_variants_dir, filename)
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta["selected"] = (filename == f"{variant_id}.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
    
    return {
        "message": "资源已选定并复制到正式目录",
        "temp_path": src_file,
        "final_path": dst_file,
        "variant_id": variant_id
    }


class AnimationRequest(BaseModel):
    """序列帧动画生成请求"""
    item_id: str
    description: str
    style: Optional[str] = "像素风"

@router.post("/{project_id}/generate-animations")
async def generate_character_animations(project_id: str, request: AnimationRequest):
    """
    为选中角色生成序列帧动画 Spritesheet
    """
    # 路径准备
    projects_dir_abs = os.path.abspath(settings.PROJECTS_DIR)
    project_path = os.path.join(projects_dir_abs, project_id)
    
    # 查找角色目录
    char_dir = os.path.join(project_path, "assets", "characters", request.item_id)
    if not os.path.exists(char_dir):
        # 如果 assets 里没有，去 temp 里看看
        char_dir = os.path.join(project_path, "temp", "characters", request.item_id)
        if not os.path.exists(char_dir):
            raise HTTPException(status_code=404, detail="找不到角色资源，请先生成或选择角色")

    # 脚本与输出路径
    anim_dir = os.path.join(project_path, "assets", "characters", request.item_id, "animations")
    os.makedirs(anim_dir, exist_ok=True)
    
    script_path = os.path.join(anim_dir, "anim_generator.py")
    output_path = os.path.join(anim_dir, "spritesheet.png")
    
    # 调用 LLM 生成动画脚本
    try:
        script_content = await llm.generate_animation_script(
            resource_id=request.item_id,
            description=request.description,
            params={"style": request.style, "size": settings.DEFAULT_IMAGE_SIZE}
        )
        
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"动画脚本生成失败: {str(e)}")
        
    # 执行脚本
    try:
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, script_path, "--output", output_path],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"动画生成失败: {result.stderr or result.stdout}")
            
        return {
            "success": True,
            "spritesheet_url": f"/assets/{project_id}/assets/characters/{request.item_id}/animations/spritesheet.png",
            "message": "序列帧动画已生成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行动画脚本异常: {str(e)}")



@router.delete("/{project_id}/{resource_type}/{resource_id}/variants/{variant_id}")
async def delete_variant(
    project_id: str, resource_type: str, resource_id: str, variant_id: str
):
    """删除一个变体"""
    if resource_type not in RESOURCE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的资源类型: {resource_type}")
    
    resource_config = RESOURCE_TYPES[resource_type]
    variants_dir = os.path.join(
        settings.PROJECTS_DIR, project_id, "assets",
        resource_config["folder"], resource_id, "variants"
    )
    
    # 删除资源文件
    resource_file = os.path.join(variants_dir, f"{variant_id}{resource_config['extension']}")
    meta_file = os.path.join(variants_dir, f"{variant_id}.json")
    
    if os.path.exists(resource_file):
        os.remove(resource_file)
    if os.path.exists(meta_file):
        os.remove(meta_file)
    
    return {"message": "变体已删除", "variant_id": variant_id}


def stylize_resource_image(input_path, output_path, style_index):
    """
    通过 Python 对原始图片进行风格化处理
    style_index: 2 (鲜艳), 3 (明亮), 4 (复古)
    """
    try:
        from PIL import Image, ImageEnhance
        with Image.open(input_path) as img:
            img = img.convert("RGBA")
            if style_index == 2:
                # 增强色彩 (鲜艳)
                img = ImageEnhance.Color(img).enhance(1.8)
            elif style_index == 3:
                # 增强亮度和对比度 (明亮)
                img = ImageEnhance.Brightness(img).enhance(1.2)
                img = ImageEnhance.Contrast(img).enhance(1.2)
            elif style_index == 4:
                # 怀旧风格 (减小饱和度并略微调暗)
                img = ImageEnhance.Color(img).enhance(0.4)
                img = ImageEnhance.Brightness(img).enhance(0.9)
            
            img.save(output_path)
            return True
    except Exception as e:
        print(f"风格化图片失败: {e}")
        return False


class GenerateItemRequest(BaseModel):
    """生成单个资源请求"""
    spec_type: str
    item_id: str
    params: Optional[Dict[str, Any]] = None
    variant_count: int = 3
    force_regenerate_script: bool = False


@router.post("/{project_id}/generate-item")
async def generate_item_resource(project_id: str, request: GenerateItemRequest):
    """
    为单个条目生成资源脚本和多个变体
    
    读取规格文件中的指定条目，生成脚本并执行，创建多个候选变体
    """
    # 规格类型与资源类型的映射
    spec_to_resource = {
        "character": "character",
        "scene": "scene", 
        "item": "item",
        "audio": "sfx",
        "ui": "ui"
    }
    
    if request.spec_type not in spec_to_resource:
        raise HTTPException(status_code=400, detail=f"不支持的规格类型: {request.spec_type}")
    
    resource_type = spec_to_resource[request.spec_type]
    resource_config = RESOURCE_TYPES[resource_type]
    
    # 获取后端绝对路径根目录
    backend_root = os.getcwd()
    
    # 路径统一使用绝对路径
    projects_dir_abs = os.path.abspath(settings.PROJECTS_DIR)
    project_path = os.path.join(projects_dir_abs, project_id)
    
    # 读取规格文件
    spec_path = os.path.join(project_path, "specs", f"{request.spec_type}.json")
    
    if not os.path.exists(spec_path):
        raise HTTPException(status_code=404, detail="规格文件不存在")
    
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_data = json.load(f)
    
    # 查找指定条目
    items = []
    if request.spec_type == "character":
        items = spec_data.get("characters", [])
    elif request.spec_type == "scene":
        items = spec_data.get("scenes", [])
    elif request.spec_type == "item":
        items = spec_data.get("items", [])
    elif request.spec_type == "audio":
        items = spec_data.get("bgm", []) + spec_data.get("sfx", [])
    elif request.spec_type == "ui":
        items = spec_data.get("elements", [])
    
    item = None
    for i in items:
        if i.get("id") == request.item_id:
            item = i
            break
    
    if not item:
        raise HTTPException(status_code=404, detail=f"找不到条目: {request.item_id}")
    
    # 获取项目风格
    project_meta_path = os.path.join(project_path, "project.json")
    art_style = "像素风"
    if os.path.exists(project_meta_path):
        with open(project_meta_path, "r", encoding="utf-8") as f:
            project_meta = json.load(f)
            art_style = project_meta.get("art_style", "像素风")
    
    # 构建描述
    if request.spec_type == "character":
        description = item.get("appearance", item.get("name", ""))
    elif request.spec_type == "scene":
        description = item.get("description", item.get("name", ""))
    elif request.spec_type == "item":
        description = item.get("appearance", item.get("description", item.get("name", "")))
    else:
        description = item.get("description", item.get("name", ""))
    
    # 合并自定义参数
    params = request.params or {}
    params.setdefault("size", settings.DEFAULT_IMAGE_SIZE)
    
    # 临时目录 - 存放脚本和候选变体 (绝对路径)
    temp_dir = os.path.join(project_path, "temp", resource_config["folder"], request.item_id)
    scripts_dir = os.path.join(temp_dir, "scripts")
    variants_dir = os.path.join(temp_dir, "variants")
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(variants_dir, exist_ok=True)
    
    # 生成主脚本 (如果不存在)
    # 每个资源条目对应一个生成器脚本
    script_filename = f"{request.item_id}_generator.py"
    main_script_path = os.path.join(scripts_dir, script_filename)
    
    # 如果请求强制重新生成脚本，先删除旧脚本
    if request.force_regenerate_script and os.path.exists(main_script_path):
        try:
            os.remove(main_script_path)
            print(f"已删除旧脚本: {main_script_path}")
        except Exception as e:
            print(f"删除旧脚本失败: {e}")
    
    # 获取项目风格
    project_meta_path = os.path.join(project_path, "project.json")
    art_style = "像素风"
    if os.path.exists(project_meta_path):
        with open(project_meta_path, "r", encoding="utf-8") as f:
            project_meta = json.load(f)
            art_style = project_meta.get("art_style", "像素风")

    # 如果脚本不存在（或已被删除），调用 LLM 生成
    if not os.path.exists(main_script_path):
        # 准备生成参数
        try:
            desc_with_style = f"{description}。美术风格：{art_style}"
            script_params = params.copy()
            script_params["style"] = art_style
            
            script_content = await llm.generate_resource_script(
                resource_type=resource_type,
                description=desc_with_style,
                params=script_params,
                category=resource_config["category"]
            )
            
            with open(main_script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"脚本生成失败: {str(e)}")
    
    # 循环生成多个变体
    variants = []
    base_resource_path = None
    
    # 强制生成 4 个候选 (1 个原版 + 3 个风格化)
    for i in range(4):
        seed = i + 1
        variant_id = f"{request.item_id}_v{seed}_{uuid.uuid4().hex[:4]}"
        output_path = os.path.join(variants_dir, f"{variant_id}{resource_config['extension']}")
        output_path_arg = output_path.replace("\\", "/")
        
        success = False
        error_msg = None
        
        # 第一个变体由脚本生成，或者音频资源全部由脚本生成
        if i == 0 or resource_config["category"] == "audio":
            import subprocess
            import sys
            cmd = [
                sys.executable, main_script_path,
                "--output", output_path_arg,
                "--seed", str(seed)
            ]
            
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=120, cwd=backend_root
                )
                success = result.returncode == 0
                if success:
                    if i == 0:
                        base_resource_path = output_path
                else:
                    error_msg = result.stderr or result.stdout or "脚本执行失败"
            except Exception as e:
                success = False
                error_msg = str(e)
        else:
            # 后续的图片变体通过 Python 进行风格化处理
            if base_resource_path and os.path.exists(base_resource_path):
                success = stylize_resource_image(base_resource_path, output_path, seed)
                if not success:
                    error_msg = "风格化处理失败"
            else:
                error_msg = "基础图片未生成，无法风格化"
        
        # 保存变体元数据
        variant_meta = {
            "variant_id": variant_id,
            "file_path": output_path,
            "script_path": main_script_path,
            "seed": seed,
            "is_selected": False,
            "success": success,
            "error": error_msg,
            "generated_at": datetime.now().isoformat()
        }
        
        meta_path = os.path.join(variants_dir, f"{variant_id}.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(variant_meta, f, indent=4, ensure_ascii=False)
            
        variants.append(variant_meta)
            
    return {
        "success": True,
        "project_id": project_id,
        "item_id": request.item_id,
        "variants": variants
    }


@router.post("/{project_id}/generate-from-spec")
async def generate_from_spec(project_id: str, spec_type: str):
    """
    从JSON规格批量生成资源
    
    根据规格类型读取对应的JSON文件，为每个条目生成资源
    """
    # 规格类型与资源类型的映射
    spec_to_resource = {
        "character": "character",
        "scene": "scene", 
        "item": "item",
        "audio": "sfx",  # 音效
        "ui": "ui"
    }
    
    if spec_type not in spec_to_resource:
        raise HTTPException(status_code=400, detail=f"不支持的规格类型: {spec_type}")
    
    resource_type = spec_to_resource[spec_type]
    
    # 读取规格文件
    spec_path = os.path.join(
        settings.PROJECTS_DIR, project_id, "specs", f"{spec_type}.json"
    )
    
    if not os.path.exists(spec_path):
        raise HTTPException(status_code=404, detail="规格文件不存在，请先提取规格")
    
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_data = json.load(f)
    
    # 获取条目列表（不同规格结构不同）
    items = []
    if spec_type == "character" and "characters" in spec_data:
        items = spec_data["characters"]
    elif spec_type == "scene" and "scenes" in spec_data:
        items = spec_data["scenes"]
    elif spec_type == "item" and "items" in spec_data:
        items = spec_data["items"]
    elif spec_type == "audio":
        # 音频可能有bgm和sfx
        items = spec_data.get("bgm", []) + spec_data.get("sfx", [])
    elif spec_type == "ui" and "elements" in spec_data:
        items = spec_data["elements"]
    
    if not items:
        raise HTTPException(status_code=400, detail="规格文件中没有可生成的条目")
    
    # 准备生成任务
    projects_dir_abs = os.path.abspath(settings.PROJECTS_DIR)
    project_path = os.path.join(projects_dir_abs, project_id)
    
    # 为每个条目生成资源脚本
    generated = []
    
    # 串行生成避免并发过高
    for item in items:
        item_id = item.get("id", str(uuid.uuid4())[:8])
        resource_config = RESOURCE_TYPES[resource_type]
        
        # 临时目录（脚本存放位置）
        temp_dir = os.path.join(project_path, "temp", resource_config["folder"], item_id)
        scripts_dir = os.path.join(temp_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        # 构建描接
        if spec_type == "character":
            description = item.get("appearance", item.get("name", ""))
        elif spec_type == "scene":
            description = item.get("description", item.get("name", ""))
        elif spec_type == "item":
            description = item.get("appearance", item.get("description", item.get("name", "")))
        elif spec_type == "audio":
            description = item.get("description", item.get("name", ""))
        elif spec_type == "ui":
            description = item.get("description", item.get("name", ""))
        else:
            description = str(item)
        
        # 获取项目风格
        project_meta_path = os.path.join(project_path, "project.json")
        art_style = "像素风"
        if os.path.exists(project_meta_path):
            with open(project_meta_path, "r", encoding="utf-8") as f:
                project_meta = json.load(f)
                art_style = project_meta.get("art_style", "像素风")
        
        # 主脚本路径
        script_filename = f"{item_id}_generator.py"
        script_path = os.path.join(scripts_dir, script_filename)
        
        # 如果脚本不存在，调用 LLM 生成
        if not os.path.exists(script_path):
            try:
                desc_with_style = f"{description}。美术风格：{art_style}"
                # 默认参数
                script_params = {"style": art_style, "size": settings.DEFAULT_IMAGE_SIZE}
                
                script_content = await llm.generate_resource_script(
                    resource_type=resource_type,
                    description=desc_with_style,
                    params=script_params,
                    category=resource_config["category"]
                )
                
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(script_content)
            except Exception as e:
                print(f"条目 {item_id} 脚本生成失败: {e}")
                continue # 跳过失败的
        
        generated.append({
            "id": item_id,
            "name": item.get("name", item_id),
            "script_path": script_path
        })
    
    return {
        "project_id": project_id,
        "spec_type": spec_type,
        "resource_type": resource_type,
        "generated_count": len(generated),
        "items": generated,
    }


@router.post("/{project_id}/run-scripts/{spec_type}")
async def run_resource_scripts(project_id: str, spec_type: str):
    """
    执行已生成的资源脚本 (批量生成默认变体)
    """
    # 规格类型与资源类型的映射
    spec_to_resource = {
        "character": "character",
        "scene": "scene", 
        "item": "item",
        "audio": "sfx",
        "ui": "ui"
    }
    
    if spec_type not in spec_to_resource:
        raise HTTPException(status_code=400, detail=f"不支持的规格类型: {spec_type}")
    
    resource_type = spec_to_resource[spec_type]
    resource_config = RESOURCE_TYPES[resource_type]
    
    projects_dir_abs = os.path.abspath(settings.PROJECTS_DIR)
    project_path = os.path.join(projects_dir_abs, project_id)
    
    # 资源temp根目录
    temp_root = os.path.join(project_path, "temp", resource_config["folder"])
    
    if not os.path.exists(temp_root):
        return {"total": 0, "success": 0, "message": "没有找到已生成的脚本目录，请先生成脚本"}
    
    # 获取后端绝对路径根目录
    backend_root = os.getcwd()
    
    results = []
    # 遍历所有 item_id 目录
    for item_id in os.listdir(temp_root):
        item_dir = os.path.join(temp_root, item_id)
        if not os.path.isdir(item_dir):
            continue
            
        scripts_dir = os.path.join(item_dir, "scripts")
        variants_dir = os.path.join(item_dir, "variants")
        os.makedirs(variants_dir, exist_ok=True)
        
        # 查找主脚本
        script_filename = f"{item_id}_generator.py"
        script_path = os.path.join(scripts_dir, script_filename)
        
        if not os.path.exists(script_path):
            continue
            
        # 生成默认变体 (seed=1)
        seed = 1
        variant_id = f"{item_id}_v{seed}_{uuid.uuid4().hex[:4]}"
        output_path = os.path.join(variants_dir, f"{variant_id}{resource_config['extension']}")
        output_path_arg = output_path.replace("\\", "/")
        
        try:
            import sys
            import subprocess
            cmd = [
                sys.executable, script_path,
                "--output", output_path_arg,
                "--seed", str(seed)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=backend_root
            )
            
            success = result.returncode == 0
            error_out = None if success else (result.stderr or result.stdout)
        except subprocess.TimeoutExpired:
            success = False
            error_out = "执行超时"
            
            # 保存元数据
            variant_meta = {
                "variant_id": variant_id,
                "file_path": output_path,
                "script_path": script_path,
                "created_at": datetime.now().isoformat(),
                "params": {"seed": seed},
                "seed": seed,
                "selected": False,
                "exists": os.path.exists(output_path),
                "error": None if success else (result.stderr or result.stdout)
            }
            
            meta_path = os.path.join(variants_dir, f"{variant_id}.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(variant_meta, f, ensure_ascii=False, indent=2)
            
            results.append({
                "script": script_filename,
                "success": success,
                "item_id": item_id
            })
            
        except Exception as e:
             results.append({
                "script": script_filename,
                "success": False,
                "output": str(e)
            })
        
    success_count = sum(1 for r in results if r["success"])
    
    return {
        "project_id": project_id,
        "spec_type": spec_type,
        "total": len(results),
        "success": success_count,
        "failed": len(results) - success_count,
        "results": results
    }


@router.get("/{project_id}/resources/{resource_type}")
async def list_resources(project_id: str, resource_type: str):
    """列出某类型的所有已生成资源"""
    if resource_type not in RESOURCE_TYPES:
        raise HTTPException(status_code=400, detail=f"无效的资源类型: {resource_type}")
    
    resource_config = RESOURCE_TYPES[resource_type]
    assets_dir = os.path.join(
        settings.PROJECTS_DIR, project_id, "assets", resource_config["folder"]
    )
    
    if not os.path.exists(assets_dir):
        return {"resources": [], "total": 0}
    
    resources = []
    for item_id in os.listdir(assets_dir):
        item_dir = os.path.join(assets_dir, item_id)
        if os.path.isdir(item_dir):
            # 查找资源文件
            resource_file = os.path.join(item_dir, f"{item_id}{resource_config['extension']}")
            if os.path.exists(resource_file):
                stat = os.stat(resource_file)
                resources.append({
                    "id": item_id,
                    "file_path": resource_file,
                    "size": stat.st_size,
                    "created_at": stat.st_mtime
                })
    
    return {
        "project_id": project_id,
        "resource_type": resource_type,
        "resources": resources,
        "total": len(resources)
    }
@router.delete("/{project_id}/temp/{spec_type}/{item_id}")
async def clear_item_temp_directory(project_id: str, spec_type: str, item_id: str):
    """
    清理特定条目的临时目录 (脚本和变体)
    """
    spec_to_resource = {
        "character": "character",
        "scene": "scene", 
        "item": "item",
        "audio": "sfx",
        "ui": "ui"
    }
    
    if spec_type not in spec_to_resource:
        raise HTTPException(status_code=400, detail=f"不支持的规格类型: {spec_type}")
    
    resource_type = spec_to_resource[spec_type]
    resource_config = RESOURCE_TYPES[resource_type]
    
    projects_dir_abs = os.path.abspath(settings.PROJECTS_DIR)
    project_path = os.path.join(projects_dir_abs, project_id)
    item_temp_dir = os.path.join(project_path, "temp", resource_config["folder"], item_id)
    
    if os.path.exists(item_temp_dir):
        try:
            import shutil
            def handle_remove_readonly(func, path, excinfo):
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            
            shutil.rmtree(item_temp_dir, onerror=handle_remove_readonly)
            return {"success": True, "message": f"条目 {item_id} 的临时缓存已清理"}
        except Exception as e:
            print(f"清理条目 {item_id} 临时目录失败: {e}")
            raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")
    else:
        return {"success": True, "message": "该条目没有临时缓存"}


@router.delete("/{project_id}/temp")
async def clear_temp_directory(project_id: str):
    """
    清理项目的临时目录 (删除所有生成脚本和变体缓存)
    """
    projects_dir_abs = os.path.abspath(settings.PROJECTS_DIR)
    project_path = os.path.join(projects_dir_abs, project_id)
    temp_dir = os.path.join(project_path, "temp")
    
    if os.path.exists(temp_dir):
        try:
            import shutil
            # Windows 下 rmtree 可能因为文件被占用而失败
            def handle_remove_readonly(func, path, excinfo):
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            
            shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
            return {"success": True, "message": "临时目录已清理"}
        except Exception as e:
            print(f"清理临时目录失败: {e}")
            raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")
    else:
        return {"success": True, "message": "临时目录不存在"}
