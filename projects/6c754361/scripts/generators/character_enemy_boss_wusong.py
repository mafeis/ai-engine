#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源生成脚本: 幻影·武松
类型: character
风格: 像素风
描述: 邪气侵蚀状态。赤裸上身，肌肉夸张，有猛虎纹身。双眼喷紫火，手持两把黑气戒刀。
"""

import os
from PIL import Image, ImageDraw
import random
import math

def generate():
    """生成像素风风格的character资源"""
    
    # 根据类型确定尺寸
    sizes = {
        "character": (64, 64),
        "scene": (320, 180),
        "item": (32, 32),
        "ui": (128, 64)
    }
    width, height = sizes.get("character", (64, 64))
    
    # 创建图片 (RGBA支持透明)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 生成调色板（像素风格）
    base_colors = [
        (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200), 255)
        for _ in range(8)
    ]
    
    # 绘制基础形状
    if "character" == "character":
        # 角色: 简单的像素人物轮廓
        # 头部
        head_color = base_colors[0]
        draw.rectangle([width//3, height//10, 2*width//3, height//3], fill=head_color)
        # 身体
        body_color = base_colors[1]  
        draw.rectangle([width//4, height//3, 3*width//4, 2*height//3], fill=body_color)
        # 腿
        leg_color = base_colors[2]
        draw.rectangle([width//4, 2*height//3, width//2-2, height-4], fill=leg_color)
        draw.rectangle([width//2+2, 2*height//3, 3*width//4, height-4], fill=leg_color)
        
    elif "character" == "scene":
        # 场景: 简单的背景层次
        # 天空/背景
        for y in range(height):
            color = (
                100 + y * 50 // height,
                120 + y * 30 // height, 
                180 - y * 50 // height,
                255
            )
            draw.line([(0, y), (width, y)], fill=color)
        # 地面
        ground_color = base_colors[3]
        draw.rectangle([0, height*2//3, width, height], fill=ground_color)
        
    elif "character" == "item":
        # 道具: 简单的图标
        center = (width//2, height//2)
        radius = min(width, height) // 3
        item_color = base_colors[4]
        draw.ellipse([
            center[0]-radius, center[1]-radius,
            center[0]+radius, center[1]+radius
        ], fill=item_color, outline=(50, 50, 50, 255))
        
    elif "character" == "ui":
        # UI: 按钮/面板样式
        bg_color = (40, 40, 60, 200)
        border_color = base_colors[5]
        draw.rectangle([2, 2, width-3, height-3], fill=bg_color, outline=border_color)
        # 高光
        draw.line([(4, 4), (width-5, 4)], fill=(255, 255, 255, 100))
    
    # 保存
    output_dir = os.path.dirname("./projects\6c754361\assets\characters\enemy_boss_wusong\enemy_boss_wusong.png")
    os.makedirs(output_dir, exist_ok=True)
    img.save("./projects\6c754361\assets\characters\enemy_boss_wusong\enemy_boss_wusong.png")
    print(f"✓ 已生成: ./projects\6c754361\assets\characters\enemy_boss_wusong\enemy_boss_wusong.png")
    return "./projects\6c754361\assets\characters\enemy_boss_wusong\enemy_boss_wusong.png"

if __name__ == "__main__":
    generate()
