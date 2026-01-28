"""
游戏控制 API

提供游戏预览实例的生命周期管理
- 启动游戏预览
- 停止游戏预览
- 获取预览状态
- WebSocket 实时通信
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict
import os
import subprocess
import psutil
import json
import asyncio
from datetime import datetime

from app.services.config import settings

router = APIRouter()


# ============ 数据模型 ============

class GameInstance(BaseModel):
    """游戏实例信息"""
    project_id: str
    process_id: Optional[int] = None
    port: int
    status: str  # stopped / starting / running / error
    started_at: Optional[str] = None
    url: Optional[str] = None


# ============ 游戏实例管理器 ============

class GameInstanceManager:
    """管理所有运行中的游戏预览实例"""
    
    def __init__(self):
        self._instances: Dict[str, Dict] = {}
        self._base_port = settings.GAME_PREVIEW_PORT
    
    def _get_available_port(self) -> int:
        """获取可用端口"""
        used_ports = {inst["port"] for inst in self._instances.values()}
        port = self._base_port
        while port in used_ports:
            port += 1
        return port
    
    async def start_preview(self, project_id: str) -> GameInstance:
        """启动游戏预览"""
        # 检查是否已在运行
        if project_id in self._instances:
            inst = self._instances[project_id]
            if inst["status"] == "running":
                return GameInstance(**inst)
        
        # 获取项目路径
        project_path = os.path.join(settings.PROJECTS_DIR, project_id)
        game_path = os.path.join(project_path, "game")
        
        if not os.path.exists(game_path):
            raise HTTPException(status_code=404, detail="游戏目录不存在")
        
        port = self._get_available_port()
        
        try:
            # 启动开发服务器 (使用 npx serve 或类似工具)
            process = subprocess.Popen(
                ["npx", "serve", "-l", str(port), game_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=game_path
            )
            
            # 等待服务启动
            await asyncio.sleep(2)
            
            if process.poll() is not None:
                raise HTTPException(status_code=500, detail="游戏启动失败")
            
            instance_info = {
                "project_id": project_id,
                "process_id": process.pid,
                "port": port,
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "url": f"http://localhost:{port}"
            }
            
            self._instances[project_id] = instance_info
            return GameInstance(**instance_info)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")
    
    async def stop_preview(self, project_id: str) -> bool:
        """停止游戏预览"""
        if project_id not in self._instances:
            return True
        
        inst = self._instances[project_id]
        pid = inst.get("process_id")
        
        if pid:
            try:
                # 终止进程及其子进程
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                
                # 等待进程结束
                parent.wait(timeout=5)
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                print(f"停止进程失败: {e}")
        
        del self._instances[project_id]
        return True
    
    def get_status(self, project_id: str) -> GameInstance:
        """获取预览状态"""
        if project_id not in self._instances:
            return GameInstance(
                project_id=project_id,
                port=0,
                status="stopped"
            )
        
        inst = self._instances[project_id]
        pid = inst.get("process_id")
        
        # 检查进程是否还在运行
        if pid:
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    return GameInstance(**inst)
            except psutil.NoSuchProcess:
                pass
        
        # 进程已结束
        del self._instances[project_id]
        return GameInstance(
            project_id=project_id,
            port=0,
            status="stopped"
        )
    
    def list_instances(self) -> list:
        """列出所有运行中的实例"""
        result = []
        for project_id in list(self._instances.keys()):
            result.append(self.get_status(project_id))
        return result


# 全局实例管理器
game_manager = GameInstanceManager()


# ============ API 端点 ============

@router.post("/{project_id}/start", response_model=GameInstance)
async def start_game_preview(project_id: str):
    """启动游戏预览"""
    return await game_manager.start_preview(project_id)


@router.post("/{project_id}/stop")
async def stop_game_preview(project_id: str):
    """停止游戏预览"""
    success = await game_manager.stop_preview(project_id)
    return {"message": "游戏已停止" if success else "停止失败", "project_id": project_id}


@router.get("/{project_id}/status", response_model=GameInstance)
async def get_game_status(project_id: str):
    """获取游戏预览状态"""
    return game_manager.get_status(project_id)


@router.get("/instances")
async def list_game_instances():
    """列出所有运行中的游戏实例"""
    instances = game_manager.list_instances()
    return {"instances": instances, "total": len(instances)}


# ============ WebSocket 实时通信 ============

class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, list] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
    
    async def broadcast(self, project_id: str, message: dict):
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


ws_manager = ConnectionManager()


@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket 端点用于实时游戏控制和状态更新
    
    消息类型:
    - start: 启动游戏
    - stop: 停止游戏
    - status: 获取状态
    - reload: 热重载
    """
    await ws_manager.connect(websocket, project_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "start":
                result = await game_manager.start_preview(project_id)
                await websocket.send_json({
                    "type": "started",
                    "data": result.model_dump()
                })
                
            elif action == "stop":
                await game_manager.stop_preview(project_id)
                await websocket.send_json({
                    "type": "stopped",
                    "project_id": project_id
                })
                
            elif action == "status":
                status = game_manager.get_status(project_id)
                await websocket.send_json({
                    "type": "status",
                    "data": status.model_dump()
                })
                
            elif action == "reload":
                # TODO: 实现热重载
                await websocket.send_json({
                    "type": "reloaded",
                    "project_id": project_id
                })
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, project_id)
