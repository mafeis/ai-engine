#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源生成脚本: 天命之人
类型: character
风格: 像素风
种子: 4
描述: 16-bit 高级像素风，约 3.5 头身。黑色短发扎小发髻，青色北斗七星抹额。内穿米白色交领长袍，外罩深蓝色无袖短褐，腰系棕色皮质腰带挂“天命星盘”。黑色束腿裤配草鞋，绑腿塞有黄色符纸。周身有金色像素粒子升起。
"""

import os
import random
from PIL import Image, ImageDraw

# 设置随机种子确保可重复性
random.seed(4)

def generate():
    width, height = (64, 64)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 生成调色板
    base_hue = random.randint(0, 360)
    colors = []
    for i in range(8):
        h = (base_hue + i * 45) % 360
        s = random.randint(60, 100) / 100
        l = random.randint(30, 70) / 100
        # HSL to RGB 简化转换
        c = (1 - abs(2*l - 1)) * s
        x = c * (1 - abs((h/60) % 2 - 1))
        m = l - c/2
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        colors.append((int((r+m)*255), int((g+m)*255), int((b+m)*255), 255))
    
    # 根据类型绘制
    if "character" == "character":
        # 头部
        draw.rectangle([width//3, height//10, 2*width//3, height//3], fill=colors[0])
        # 身体
        draw.rectangle([width//4, height//3, 3*width//4, 2*height//3], fill=colors[1])
        # 腿
        draw.rectangle([width//4, 2*height//3, width//2-2, height-4], fill=colors[2])
        draw.rectangle([width//2+2, 2*height//3, 3*width//4, height-4], fill=colors[2])
        # 眼睛
        draw.rectangle([width//3+4, height//6, width//3+8, height//6+4], fill=(255,255,255,255))
        draw.rectangle([2*width//3-8, height//6, 2*width//3-4, height//6+4], fill=(255,255,255,255))
        
    elif "character" == "scene":
        # 天空渐变
        for y in range(height*2//3):
            ratio = y / (height*2//3)
            r = int(colors[6][0] * (1-ratio) + colors[7][0] * ratio)
            g = int(colors[6][1] * (1-ratio) + colors[7][1] * ratio)
            b = int(colors[6][2] * (1-ratio) + colors[7][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        # 地面
        draw.rectangle([0, height*2//3, width, height], fill=colors[3])
        # 装饰物
        for _ in range(random.randint(3, 6)):
            x = random.randint(0, width)
            h = random.randint(10, 30)
            draw.rectangle([x-5, height*2//3-h, x+5, height*2//3], fill=colors[4])
        
    elif "character" == "item":
        cx, cy = width//2, height//2
        r = min(width, height) // 3
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=colors[4], outline=colors[5])
        # 高光
        draw.arc([cx-r+2, cy-r+2, cx+r-2, cy+r-2], 200, 340, fill=(255,255,255,200), width=2)
        
    elif "character" == "ui":
        # 面板背景
        draw.rectangle([2, 2, width-3, height-3], fill=(40, 40, 60, 220), outline=colors[5])
        # 高光线
        draw.line([(4, 4), (width-5, 4)], fill=(255, 255, 255, 100))
        draw.line([(4, 5), (width-5, 5)], fill=(200, 200, 255, 50))
    
    # 保存
    os.makedirs(os.path.dirname("./projects\6c754361\assets\characters\protagonist_109th_star\variants\protagonist_109th_star_v4_d03c.png"), exist_ok=True)
    img.save("./projects\6c754361\assets\characters\protagonist_109th_star\variants\protagonist_109th_star_v4_d03c.png")
    print(f"✓ 已生成: ./projects\6c754361\assets\characters\protagonist_109th_star\variants\protagonist_109th_star_v4_d03c.png")

if __name__ == "__main__":
    generate()
