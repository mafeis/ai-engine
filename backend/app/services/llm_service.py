"""
LLM 服务

封装与本地部署 LLM 的交互
- 文档生成
- 规格提取
- 资源脚本生成
"""

import httpx
from typing import Dict, Any, Optional
import json

from app.services.config import settings


class LLMService:
    """本地 LLM 服务客户端"""
    
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.api_key = settings.LLM_API_KEY
    
    async def _chat_completion(
        self, 
        messages: list, 
        temperature: float = 0.7,
        max_tokens: int = 8192  # 增加上限防止生成代码时被截断
    ) -> str:
        """调用 LLM Chat Completion API"""
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def generate_document(
        self,
        project_name: str,
        project_intro: str,
        game_type: str,
        art_style: str,
        doc_type: str
    ) -> str:
        """
        生成游戏设计文档
        
        Args:
            project_name: 游戏名称
            project_intro: 游戏简介
            game_type: 游戏类型
            art_style: 美术风格
            doc_type: 文档类型
        
        Returns:
            Markdown 格式的设计文档
        """
        # 文档类型对应的 Prompt 模板
        prompts = {
            "main": f"""你是一位专业的游戏策划，请根据以下信息创建一份完整的游戏设计文档。

游戏名称: {project_name}
游戏简介: {project_intro}
游戏类型: {game_type}
美术风格: {art_style}

请创建包含以下章节的 Markdown 文档:
1. 游戏概述 (类型、受众、核心玩法、独特卖点)
2. 世界观背景 (时代背景、主要势力、核心冲突)
3. 核心系统 (战斗/成长/经济/社交系统概述)
4. 技术规格 (目标平台、分辨率、帧率)
5. 开发里程碑

请用中文撰写，内容要专业、详细、可执行。""",

            "character": f"""你是一位专业的游戏角色设计师，请根据以下游戏信息创建角色设计文档。

游戏名称: {project_name}
游戏简介: {project_intro}
美术风格: {art_style}

请创建包含以下内容的 Markdown 文档:
1. 主角设计 (外观描述、性格特点、背景故事、技能列表)
2. NPC 设计 (关键 NPC 列表，每个包含外观和作用)
3. 敌人设计 (敌人类型列表，每个包含外观、战斗方式、掉落物)
4. 视觉风格指南 (配色方案、比例规范、动画需求)

每个角色需要包含详细的自然语言外观描述，用于后续 AI 生成资源。""",

            "gameplay": f"""你是一位专业的游戏玩法设计师，请根据以下游戏信息创建玩法设计文档。

游戏名称: {project_name}
游戏简介: {project_intro}
游戏类型: {game_type}

请创建包含以下内容的 Markdown 文档:
1. 核心玩法循环 (主要游戏循环描述)
2. 控制方案 (键盘/触屏/手柄映射)
3. 战斗系统 (攻击、技能、连击、格挡等)
4. 进度系统 (等级、经验、解锁机制)
5. 难度曲线 (各阶段难度设计)
6. 数值平衡 (关键数值范围定义)""",

            "scene": f"""你是一位专业的游戏场景设计师，请根据以下游戏信息创建场景设计文档。
    
游戏名称: {project_name}
游戏简介: {project_intro}
美术风格: {art_style}

请创建包含以下内容的 Markdown 文档:
1. 场景列表: 每个场景需包含：
   - 名称与基本描述
   - 场景总尺寸 (如 1920x1080)
   - **布局布局 (Layout Structure)**: 详细描述场景的区域划分（如：左侧是森林，中间是祭坛，背景是雪山）。
   - **地块与物件清单**: 列出该场景中包含的所有静态建筑、植被、装饰物及其相对位置描述。
2. 场景流转图 (场景间的连接关系)
3. 视觉气氛 (每个场景的主色调、光照强度)
4. 背景音乐建议

每个场景描述必须足够详细，不仅仅是描述，而要包含“空间布局”的信息，例如：“中央是一个 400x400 的石砌广场，广场北侧紧挨着两座哥特式箭塔”。""",

            "item": f"""你是一位专业的游戏道具设计师，请根据以下游戏信息创建道具设计文档。

游戏名称: {project_name}
游戏简介: {project_intro}
美术风格: {art_style}

请创建包含以下内容的 Markdown 文档:
1. 道具分类 (武器/装备/消耗品/关键道具等)
2. 道具列表 (每个道具包含名称、外观描述、效果、稀有度)
3. 获取方式 (掉落/商店/制作/任务奖励)
4. 道具经济 (价格范围、掉落率)

每个道具需要详细的自然语言外观描述，用于后续 AI 生成。""",

            "quest": f"""你是一位专业的游戏任务设计师，请根据以下游戏信息创建任务设计文档。

游戏名称: {project_name}
游戏简介: {project_intro}

请创建包含以下内容的 Markdown 文档:
1. 主线任务 (任务链，每个任务包含目标、触发条件、奖励)
2. 支线任务 (可选任务列表)
3. 日常/重复任务 (如有)
4. 成就系统 (成就列表及解锁条件)
5. 任务对话 (关键任务的对话文本)""",

            "ui": f"""你是一位专业的游戏 UI 设计师，请根据以下游戏信息创建 UI 设计文档。

游戏名称: {project_name}
美术风格: {art_style}

请创建包含以下内容的 Markdown 文档:
1. UI 风格定义 (整体风格、配色、字体)
2. 界面列表:
   - 主菜单
   - HUD (血量、技能栏、小地图等)
   - 背包界面
   - 角色信息界面
   - 设置界面
   - 对话界面
3. 每个界面的布局描述和元素列表
4. 按钮/图标设计规范

每个 UI 元素需要详细的自然语言描述，用于后续 AI 生成。""",

            "audio": f"""你是一位专业的游戏音频设计师，请根据以下游戏信息创建音频设计文档。

游戏名称: {project_name}
游戏简介: {project_intro}

请创建包含以下内容的 Markdown 文档:
1. 背景音乐列表:
   - 场景BGM (每个场景对应的音乐风格描述)
   - 战斗BGM
   - 特殊事件BGM
2. 音效列表:
   - 角色音效 (脚步、攻击、受伤、死亡等)
   - 环境音效 (风声、雨声等)
   - UI 音效 (点击、确认、取消等)
   - 道具音效 (拾取、使用等)
3. 语音 (如有)

每个音频需要详细的自然语言描述，用于后续 AI 生成。"""
        }
        
        prompt = prompts.get(doc_type, prompts["main"])
        
        messages = [
            {"role": "system", "content": "你是一位经验丰富的游戏设计师，精通各类游戏的策划文档编写。"},
            {"role": "user", "content": prompt}
        ]
        
        return await self._chat_completion(messages, temperature=0.7)
    
    async def extract_spec(self, doc_content: str, doc_type: str) -> Dict[str, Any]:
        """
        从设计文档中提取 JSON 规格
        
        Args:
            doc_content: Markdown 文档内容
            doc_type: 文档类型
        
        Returns:
            结构化 JSON 数据
        """
        # JSON Schema 模板
        schemas = {
            "character": """{
  "characters": [
    {
      "id": "string",
      "name": "string",
      "type": "protagonist|npc|enemy",
      "appearance": "自然语言描述",
      "stats": {"hp": 100, "attack": 10, "defense": 5, "speed": 5},
      "skills": [{"id": "string", "name": "string", "damage": 0, "cooldown": 0}],
      "animations": ["idle", "walk", "attack", "hurt", "death"]
    }
  ]
}""",
            "scene": """{
  "scenes": [
    {
      "id": "string",
      "name": "string",
      "width": 1920,
      "height": 1080,
      "layout_description": "详细的布局描述，包含地貌分布、建筑位置等",
      "grid_info": {"rows": 8, "cols": 12, "cell_size": 128},
      "elements": [
        {
            "name": "元素名称",
            "type": "building|tree|rock|platform|water", 
            "rect": {"x": 0, "y": 0, "w": 100, "h": 100},
            "description": "视觉细节描述"
        }
      ],
      "background_color": "#000000",
      "connections": ["scene_id_1"],
      "bgm_id": "string"
    }
  ]
}""",
            "item": """{
  "items": [
    {
      "id": "string",
      "name": "string",
      "category": "weapon|armor|consumable|key",
      "appearance": "自然语言描述",
      "rarity": "common|rare|epic|legendary",
      "effects": [{"type": "heal|damage|buff", "value": 0}],
      "price": 100,
      "drop_rate": 0.1
    }
  ]
}""",
            "audio": """{
  "bgm": [
    {
      "id": "string",
      "name": "string",
      "description": "自然语言描述",
      "duration": 60,
      "tempo": "slow|medium|fast",
      "mood": "string"
    }
  ],
  "sfx": [
    {
      "id": "string",
      "name": "string",
      "description": "自然语言描述",
      "duration": 1.0,
      "category": "character|environment|ui|item"
    }
  ]
}"""
        }
        
        schema = schemas.get(doc_type, "{}")
        
        prompt = f"""请从以下游戏设计文档中提取结构化数据，输出 JSON 格式。

设计文档:
{doc_content}

期望的 JSON 结构:
{schema}

请只输出 JSON 数据，不要有其他内容。确保:
1. 所有字段都有合理的值
2. appearance/description 字段保留详细的自然语言描述
3. 数值字段使用合理的游戏数值"""

        messages = [
            {"role": "system", "content": "你是一个数据提取助手，只输出有效的 JSON 数据，不要其他解释。"},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._chat_completion(messages, temperature=0.2)
        
        # 尝试解析 JSON
        try:
            # 清理可能的 Markdown 代码块
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            return json.loads(result.strip())
        except json.JSONDecodeError:
            return {"raw": result, "error": "JSON 解析失败，请手动调整"}
    
    async def generate_resource_script(
        self,
        resource_type: str,
        description: str,
        params: Dict[str, Any],
        category: str
    ) -> str:
        """
        生成资源创建 Python 脚本
        
        Args:
            resource_type: 资源类型
            description: 自然语言描述
            params: 生成参数
            category: 类别 (image/audio)
        
        Returns:
            可执行的 Python 脚本代码
        """
        if resource_type == "scene":
            # 场景生成：基于布局描述和元素列表
            prompt = f"""请生成一个 Python 脚本，使用 PIL (Pillow) 库绘制以下 场景布局简图 (Layout Map)。

场景条目: {params.get('name', '未命名场景')}
尺寸: {params.get('width', 1920)}x{params.get('height', 1080)} 像素
核心布局描述: {params.get('layout_description', '未提供')}
网格信息: {params.get('grid_info', '未提供')}
美术风格: {params.get('style', 'pixel')}

元素清单 (elements):
{json.dumps(params.get('elements', []), ensure_ascii=False, indent=2)}

要求:
1. **脚本接口**: 必须接受 --output 和 --seed (整数) 两个命令行参数。使用 `random.seed(args.seed)`。
2. **绘制核心 ( layout_map )**:
   - 这是一个“宏观布局图”。
   - **背景**: 根据 `background_color` ({params.get('background_color', '#000000')}) 填充底色。
   - **地貌绘制**: 根据 `layout_description` 绘制大的地形色块（如左侧深绿色森林区，底部灰色高原等）。
   - **建筑与物品绘制**: 遍历 `elements` 数组，在指定的 `rect` (x, y, w, h) 位置绘制对应的占位色块。
     - 如果 type 是 building，绘制一个具象化的简易外轮廓。
     - 如果 type 是 water/river，绘制蓝色调的色块。
   - **标注**: 在重要元素中心位置用 `draw.text` 标注其 `name`。
3. **视觉表现**: 
   - 增加简单的渐变或纹理，使布局图看起来像是一张专业的设计草图或“关卡俯视图”。
   - 确保所有坐标计算严谨。
4. **输出**: 保存为 RGBA PNG。

代码质量: 包含完整的 import，添加详细中文注释。确保代码在 `if __name__ == '__main__': main()` 中执行。"""
        
        elif category == "image":
            prompt = f"""请生成一个 Python 脚本，使用 PIL (Pillow) 库绘制以下图像资源。

资源类型: {resource_type}
描述: {description}
参数:
- 尺寸: {params.get('size', 64)}x{params.get('size', 64)} 像素
- 风格: {params.get('style', 'pixel')} (像素风)

要求:
1. **脚本接口**: 必须接受 --output 和 --seed (整数) 两个命令行参数。
2. **随机性与变体**: 必须使用 `random.seed(args.seed)`。种子必须显著影响生成结果。不同的种子应该产生完全不同的视觉方案。
3. **坐标安全 (重要)**: 确保所有 `draw.ellipse`, `draw.rectangle` 等调用的坐标满足 [x0, y0, x1, y1] 中 x0 < x1 且 y0 < y1。
4. **算法级逻辑**:
   - **分层绘制**: 1. 投影/阴影；2. 基础轮廓；3. 高光与细节。
   - **纹理处理**: 使用循环在绘制好的形状内随机添加像素级的颜色偏差（Texture Noise），增加质感。
5. **视觉表现**: 背景必须透明 (RGBA)。
6. **代码规范**: 完整导入，详细中文注释。在 `if __name__ == '__main__':` 中执行。

示例结构:
```python
import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--seed', type=int, default=1)
    args = parser.parse_args()
    random.seed(args.seed)
    # ... 绘图逻辑 ...
    # img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()
```
请只输出代码。"""

        else:  # audio
            prompt = f"""请生成一个 Python 脚本，使用 numpy 和 scipy 库生成以下音频资源。

资源类型: {resource_type}
描述: {description}
参数:
- 时长: {params.get('duration', 2.0)} 秒
- 采样率: {params.get('sample_rate', 44100)} Hz

要求:
1. 脚本需要接受 --output 命令行参数指定输出路径
2. 使用 numpy 生成波形数据
3. 使用 scipy.io.wavfile 保存为 WAV 格式
4. 代码要完整可执行
5. 根据描述选择合适的波形（正弦波、方波、噪声等）和包络
6. 添加中文注释

示例脚本结构:
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
{resource_type}音频生成脚本
描述: {description}
\"\"\"
import argparse
import numpy as np
from scipy.io import wavfile

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    sample_rate = {params.get('sample_rate', 44100)}
    duration = {params.get('duration', 2.0)}
    
    # 生成音频数据
    t = np.linspace(0, duration, int(sample_rate * duration))
    # ...
    
    wavfile.write(args.output, sample_rate, audio_data)
    print(f'已保存到: {{args.output}}')

if __name__ == '__main__':
    main()
```

请根据描述生成完整的音频生成代码。"""

        messages = [
            {"role": "system", "content": "你是一个严谨的 Python 专家。生成的代码必须语法完美，括号必须闭合，变量必须先定义再使用。只输出代码，不要任何解释。"},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._chat_completion(messages, temperature=0.1, max_tokens=8192)
        
        # 清理可能的 Markdown 代码块
        if "```python" in result:
            result = result.split("```python")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        return result.strip()
    async def generate_animation_script(
        self, 
        resource_id: str,
        description: str,
        params: dict
    ) -> str:
        """
        生成角色动画序列帧脚本 (Spritesheet)
        """
        prompt = f"""请生成一个 Python 脚本，使用 PIL (Pillow) 库为以下角色绘制【序列帧动画序列图 (Spritesheet)】。

角色 ID: {resource_id}
角色描述: {description}
美术风格: {params.get('style', '像素风')}
单帧尺寸: {params.get('size', 64)}x{params.get('size', 64)} 像素

要求：
1. **脚本接口**: 必须接受 `--output` 参数指定结果图片的保存路径。
2. **Spritesheet 结构**: 
   - 最终图片是一个大图（Atlas/Spritesheet）。
   - 包含 3 行动作：
     - 第一行: **Idle (待机)** - 至少 4 帧。
     - 第二行: **Walk (行走)** - 至少 4 帧。
     - 第三行: **Attack (攻击)** - 至少 4 帧。
   - 总输出尺寸应为: (4 * 单帧宽) x (3 * 单帧高)。
3. **动画实现**: 
   - 通过在每一帧中微调角色的肢体位置、高度或形状来实现动画效果。
   - 行走动画应包含腿部和手臂的交替摆动。
   - 攻击动画应包含蓄力、挥动/发射、收招的过程。
4. **一致性**: 确保所有动作中的角色外观（颜色、服装、体型）严格一致。
5. **代码质量**:
   - 包含完整的 import。
   - 使用 RGBA 透明背景。
   - 坐标计算严谨，防止溢出。

示例代码逻辑:
```python
import argparse
from PIL import Image, ImageDraw

def draw_frame(draw, x_offset, y_offset, action, frame_idx, char_params):
    # 根据动作和帧索引绘制角色
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    # 创建大图 (4帧 x 3行动作)
    sheet = Image.new('RGBA', (64*4, 64*3), (0,0,0,0))
    # ... 循环调用 draw_frame ...
    sheet.save(args.output)
```
请根据角色描述，发挥创意通过 PIL 的几何图形组合绘制出一套精美的 2D 动画序列图。"""

        messages = [
            {"role": "system", "content": "你是一个严谨的游戏资源生成专家。你擅长使用 PIL 编写复杂的 2D 动画生成脚本。只输出代码，不要解释。"},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._chat_completion(messages, temperature=0.2, max_tokens=8192)
        
        # 清理 Markdown 代码块
        if "```python" in result:
            result = result.split("```python")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
            
        return result.strip()
