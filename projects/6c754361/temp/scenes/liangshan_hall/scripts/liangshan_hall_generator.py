import argparse
import random
from PIL import Image, ImageDraw, ImageFont

def main():
    # 1. 脚本接口: 处理命令行参数
    parser = argparse.ArgumentParser(description="生成梁山泊·聚义厅场景布局简图")
    parser.add_argument("--output", type=str, required=True, help="输出图像的绝对路径")
    parser.add_argument("--seed", type=int, required=True, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 2. 场景基础信息
    width, height = 1280, 720
    bg_color = "#4B3621"  # 深木色/深褐色背景
    grid_info = {'rows': 10, 'cols': 18, 'cell_size': 72}
    
    # 元素清单
    elements = [
        {
            "name": "替天行道大旗",
            "type": "building",
            "rect": {"x": 540, "y": 50, "w": 200, "h": 300},
            "color": (255, 215, 0, 200),  # 杏黄色
            "description": "巨大的杏黄旗"
        },
        {
            "name": "头领交椅",
            "type": "platform",
            "rect": {"x": 100, "y": 400, "w": 1080, "h": 200},
            "color": (139, 69, 19, 180),  # 红褐色木质
            "description": "分列两旁的厚重木椅"
        },
        {
            "name": "战略沙盘",
            "type": "rock",
            "rect": {"x": 590, "y": 450, "w": 100, "h": 80},
            "color": (128, 128, 128, 220),  # 石灰色
            "description": "石制沙盘"
        },
        {
            "name": "篝火堆",
            "type": "water",  # 根据要求，type为water绘制蓝色调
            "rect": {"x": 300, "y": 500, "w": 60, "h": 60},
            "color": (0, 191, 255, 200),  # 虽为篝火，按要求type=water绘蓝色
            "description": "跳动的像素火焰"
        }
    ]

    # 3. 创建画布
    image = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # 4. 绘制地貌 (粗糙石砖地面纹理)
    cell_size = grid_info['cell_size']
    for r in range(grid_info['rows']):
        for c in range(grid_info['cols']):
            x1 = c * cell_size
            y1 = r * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            
            # 随机偏移色值模拟石砖质感
            offset = random.randint(-10, 10)
            stone_color = (60 + offset, 60 + offset, 65 + offset)
            draw.rectangle([x1, y1, x2, y2], fill=stone_color, outline=(40, 40, 40))
            
            # 增加像素风杂色点
            for _ in range(5):
                px = random.randint(x1, x2-1)
                py = random.randint(y1, y2-1)
                draw.point((px, py), fill=(80, 80, 80))

    # 5. 绘制远景 (大门外的梁山湖泊)
    # 在顶部中央绘制一个代表大门的区域，透出湖泊水汽
    gate_rect = [440, 0, 840, 40]
    draw.rectangle(gate_rect, fill=(100, 149, 237, 150)) # 水蓝色

    # 6. 遍历绘制元素
    try:
        font = ImageFont.load_default()
    except:
        font = None

    for item in elements:
        rect = item['rect']
        x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
        shape_type = item['type']
        color = item['color']

        if shape_type == "building":
            # 绘制大旗外轮廓 (具象化：旗杆+旗面)
            draw.rectangle([x + w//2 - 5, y, x + w//2 + 5, y + h], fill=(101, 67, 33)) # 旗杆
            draw.polygon([(x, y), (x + w, y + h//3), (x, y + h//2)], fill=color, outline=(0, 0, 0))
        
        elif shape_type == "water":
            # 绘制蓝色调色块 (篝火按要求处理)
            draw.ellipse([x, y, x + w, y + h], fill=color, outline=(255, 255, 255))
            
        elif shape_type == "platform":
            # 绘制交椅区域 (长条形)
            draw.rectangle([x, y, x + w, y + h], fill=color, outline=(50, 20, 0), width=3)
            # 内部细分小椅子占位
            for i in range(10):
                chair_x = x + (i * (w // 10)) + 10
                draw.rectangle([chair_x, y + 10, chair_x + 40, y + 50], fill=(90, 40, 10))

        elif shape_type == "rock":
            # 绘制沙盘 (石制)
            draw.rectangle([x, y, x + w, y + h], fill=color, outline=(30, 30, 30))
            draw.rectangle([x + 10, y + 10, x + w - 10, y + h - 10], fill=(34, 139, 34)) # 沙盘上的绿地

        # 7. 标注名称
        text_pos = (x + w // 2, y + h // 2)
        if font:
            # 获取文字大小以居中
            text_bbox = draw.textbbox((0, 0), item['name'], font=font)
            tw = text_bbox[2] - text_bbox[0]
            th = text_bbox[3] - text_bbox[1]
            draw.text((text_pos[0] - tw // 2, text_pos[1] - th // 2), item['name'], fill=(255, 255, 255), font=font)

    # 8. 增加高对比度阴影效果 (简单渐变模拟)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for i in range(0, height, 4):
        alpha = int(100 * (i / height))
        overlay_draw.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))
    image = Image.alpha_composite(image, overlay)

    # 9. 输出保存
    image.save(args.output, "PNG")

if __name__ == "__main__":
    main()