import argparse
import random
import os
from PIL import Image, ImageDraw, ImageFont

def main():
    # 1. 脚本接口与参数解析
    parser = argparse.ArgumentParser(description="生成花果山·水帘洞前场景布局简图")
    parser.add_argument("--output", type=str, required=True, help="输出文件路径 (例如: layout.png)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 2. 场景基础配置
    width, height = 3840, 1080
    bg_color = "#90EE90"  # 浅绿色背景
    grid_info = {'rows': 9, 'cols': 30, 'cell_size': 128}
    
    # 元素清单
    elements = [
        {
            "name": "水帘洞瀑布",
            "type": "building",
            "rect": {"x": 1920, "y": 540, "w": 800, "h": 1080},
            "description": "核心建筑，包含动态粒子效果的水帘。"
        },
        {
            "name": "半圆形石台",
            "type": "platform",
            "rect": {"x": 1620, "y": 780, "w": 600, "h": 300},
            "description": "位于瀑布前的核心交互区域。"
        },
        {
            "name": "仙桃树",
            "type": "tree",
            "rect": {"x": 300, "y": 680, "w": 200, "h": 400},
            "description": "巨大的桃树，左侧共5棵。"
        },
        {
            "name": "弹跳蘑菇",
            "type": "platform",
            "rect": {"x": 1500, "y": 980, "w": 100, "h": 100},
            "description": "全场景分布的可交互物件。"
        },
        {
            "name": "猴王宝座",
            "type": "rock",
            "rect": {"x": 600, "y": 800, "w": 300, "h": 200},
            "description": "巨大的石制宝座。"
        },
        {
            "name": "紫色藤蔓",
            "type": "platform",
            "rect": {"x": 2800, "y": 200, "w": 50, "h": 600},
            "description": "背景中散落的10根可攀爬藤蔓。"
        }
    ]

    # 3. 创建画布
    image = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # 4. 绘制地貌 (宏观布局)
    # 左侧生活区 (0-1200): 平缓森林
    draw.rectangle([0, 0, 1200, height], fill="#76CC76")
    for _ in range(20):
        x = random.randint(0, 1100)
        y = random.randint(0, height-100)
        draw.ellipse([x, y, x+150, y+100], fill="#66BB66")

    # 中间核心区 (1200-2600): 水域与石台基座
    draw.rectangle([1200, 0, 2600, height], fill="#87CEEB") # 浅蓝色水域感
    draw.rectangle([1200, 800, 2600, height], fill="#A9A9A9") # 底部石质基座

    # 右侧修行区 (2600-3840): 高地
    draw.rectangle([2600, 0, 3840, height], fill="#556B2F") # 深橄榄绿
    # 绘制阶梯状高地
    for i in range(5):
        h_step = 200 + i * 150
        draw.rectangle([2600 + i*250, height - h_step, 3840, height], fill="#6B8E23")

    # 5. 绘制网格线 (辅助视觉)
    grid_color = (0, 0, 0, 30)
    for c in range(grid_info['cols'] + 1):
        x = c * grid_info['cell_size']
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for r in range(grid_info['rows'] + 1):
        y = r * grid_info['cell_size']
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # 6. 绘制元素
    try:
        # 尝试加载中文字体，若失败则使用默认
        font = ImageFont.truetype("simhei.ttf", 40)
    except:
        font = ImageFont.load_default()

    for el in elements:
        rect = el['rect']
        name = el['name']
        etype = el['type']
        
        # 计算左上角和右下角 (假设 rect 的 x,y 是中心点)
        left = rect['x'] - rect['w'] // 2
        top = rect['y'] - rect['h'] // 2
        right = rect['x'] + rect['w'] // 2
        bottom = rect['y'] + rect['h'] // 2

        if etype == "building": # 瀑布
            # 绘制主体
            draw.rectangle([left, top, right, bottom], fill="#00BFFF", outline="#FFFFFF", width=5)
            # 绘制水纹线条
            for i in range(10):
                lx = left + (i * rect['w'] // 10)
                draw.line([(lx, top), (lx, bottom)], fill="#F0F8FF", width=2)
        
        elif etype == "platform": # 石台、蘑菇、藤蔓
            if "石台" in name:
                draw.chord([left, top, right, bottom + rect['h']], 180, 360, fill="#D3D3D3", outline="#444444", width=3)
            elif "蘑菇" in name:
                draw.ellipse([left, top, right, bottom], fill="#FF4500", outline="#FFFFFF", width=2)
                draw.ellipse([left+20, top+20, left+40, top+40], fill="white")
            elif "藤蔓" in name:
                draw.rectangle([left, top, right, bottom], fill="#8A2BE2")
                # 绘制额外9根
                for _ in range(9):
                    rx = random.randint(2600, 3800)
                    ry = random.randint(100, 400)
                    draw.rectangle([rx, ry, rx+10, ry+500], fill="#8A2BE2")

        elif etype == "tree": # 仙桃树
            # 树干
            draw.rectangle([rect['x']-20, rect['y'], rect['x']+20, bottom], fill="#8B4513")
            # 树冠
            draw.ellipse([left, top, right, top + rect['h']//2], fill="#FFB6C1", outline="#FF69B4", width=3)
            # 绘制额外4棵
            for _ in range(4):
                tx = random.randint(100, 1000)
                ty = random.randint(500, 800)
                draw.rectangle([tx-10, ty, tx+10, ty+100], fill="#8B4513")
                draw.ellipse([tx-50, ty-80, tx+50, ty+20], fill="#FFB6C1")

        elif etype == "rock": # 宝座
            draw.polygon([(left, bottom), (right, bottom), (rect['x'], top)], fill="#808080", outline="#333333")

        # 绘制标注文字
        text_pos = (rect['x'], rect['y'])
        draw.text(text_pos, name, fill="black", font=font, anchor="mm")

    # 7. 增加装饰性边框和标题
    draw.rectangle([0, 0, width-1, height-1], outline="#2F4F4F", width=10)
    draw.text((50, 50), "场景布局图: 花果山·水帘洞前 (3840x1080)", fill="#2F4F4F", font=font)

    # 8. 保存输出
    image.save(args.output)
    print(f"Layout map saved to {args.output}")

if __name__ == "__main__":
    main()