import argparse
import random
from PIL import Image, ImageDraw, ImageFont

def main():
    # 1. 命令行参数解析
    parser = argparse.ArgumentParser(description="生成景阳冈·密林场景布局简图")
    parser.add_argument("--output", type=str, required=True, help="输出图片的绝对路径")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 2. 场景基础配置
    width = 2560
    height = 480
    background_color = (26, 36, 33, 255)  # #1A2421
    grid_info = {'rows': 6, 'cols': 32, 'cell_size': 80}
    
    # 元素清单
    elements = [
        {
            "name": "枯树枝堆",
            "type": "rock",
            "rect": {"x": 400, "y": 400, "w": 120, "h": 40},
            "description": "踩踏后会触发清脆断裂声"
        },
        {
            "name": "猎人陷阱",
            "type": "platform",
            "rect": {"x": 1200, "y": 420, "w": 80, "h": 20},
            "description": "隐藏在枯叶下的夹子"
        },
        {
            "name": "官府告示牌",
            "type": "building",
            "rect": {"x": 100, "y": 300, "w": 60, "h": 100},
            "description": "破旧的木牌"
        }
    ]

    # 3. 创建画布
    image = Image.new("RGBA", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # 4. 绘制背景装饰 (深邃密林感)
    # 绘制远景树木阴影
    for _ in range(50):
        tree_w = random.randint(40, 100)
        tree_h = random.randint(200, 400)
        tx = random.randint(0, width)
        ty = height - tree_h - random.randint(0, 50)
        # 使用半透明深绿色
        draw.rectangle([tx, ty, tx + tree_w, height], fill=(15, 25, 20, 150))

    # 5. 绘制地貌 (起伏不平的地势)
    ground_points = [(0, height)]
    current_x = 0
    while current_x < width:
        current_x += random.randint(50, 150)
        current_y = height - random.randint(20, 60)
        ground_points.append((current_x, current_y))
    ground_points.append((width, height))
    # 填充地面色块 (深灰褐色)
    draw.polygon(ground_points, fill=(45, 40, 35, 255))

    # 6. 绘制网格 (辅助线)
    grid_color = (255, 255, 255, 15)
    for c in range(grid_info['cols'] + 1):
        x = c * grid_info['cell_size']
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for r in range(grid_info['rows'] + 1):
        y = r * grid_info['cell_size']
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # 7. 绘制元素 (Elements)
    try:
        # 尝试加载字体，如果失败则使用默认
        font = ImageFont.load_default()
    except Exception:
        font = None

    for item in elements:
        rect = item['rect']
        x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
        name = item['name']
        etype = item['type']

        if etype == "building":
            # 绘制告示牌形状
            draw.rectangle([x + w*0.4, y + h*0.6, x + w*0.6, y + h], fill=(101, 67, 33, 255)) # 杆子
            draw.rectangle([x, y, x + w, y + h*0.6], fill=(139, 90, 43, 255), outline=(60, 40, 20, 255)) # 牌面
        elif etype == "rock":
            # 绘制枯树枝堆 (不规则形状)
            draw.ellipse([x, y, x + w, y + h], fill=(80, 70, 60, 255), outline=(40, 35, 30, 255))
            for _ in range(5): # 增加一些线条表现枝干
                lx1 = random.randint(x, x+w)
                ly1 = random.randint(y, y+h)
                draw.line([lx1, ly1, lx1 + 20, ly1 - 10], fill=(50, 40, 30, 255), width=2)
        elif etype == "platform":
            # 绘制陷阱 (金属质感)
            draw.rectangle([x, y, x + w, y + h], fill=(120, 120, 120, 255), outline=(50, 50, 50, 255))
            draw.line([x, y + h//2, x + w, y + h//2], fill=(80, 80, 80, 255), width=1)
        elif etype == "water":
            draw.rectangle([x, y, x + w, y + h], fill=(30, 60, 100, 180))

        # 绘制标注文字
        text_pos = (x + 5, y - 20)
        draw.text(text_pos, name, fill=(200, 200, 200, 255), font=font)

    # 8. 绘制浓雾层 (穿梭林间的雾气)
    fog_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog_overlay)
    for _ in range(15):
        fx = random.randint(-200, width)
        fy = random.randint(100, 400)
        fw = random.randint(400, 800)
        fh = random.randint(50, 150)
        # 绘制长条状半透明椭圆模拟雾气
        fog_draw.ellipse([fx, fy, fx + fw, fy + fh], fill=(200, 210, 200, 30))
    
    # 合并雾气层
    image = Image.alpha_composite(image, fog_overlay)

    # 9. 增加边缘暗角 (Vignette) 提升氛围
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    # 顶部和底部渐变暗化
    for i in range(100):
        alpha = int(150 * (1 - i/100))
        v_draw.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))
        v_draw.line([(0, height - i), (width, height - i)], fill=(0, 0, 0, alpha))
    
    image = Image.alpha_composite(image, vignette)

    # 10. 保存输出
    image.save(args.output, "PNG")

if __name__ == "__main__":
    main()