import argparse
import random
import os
from PIL import Image, ImageDraw, ImageFont

def draw_layout_map(output_path, seed):
    """
    绘制东京汴梁·闹市场景布局简图
    """
    # 设置随机种子
    random.seed(seed)

    # 基础参数
    width, height = 1920, 1080
    rows, cols = 9, 16
    cell_size = 120
    bg_color = (139, 69, 19, 255)  # #8B4513 SaddleBrown
    
    # 创建画布
    image = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # 1. 绘制背景纹理 (像素风颗粒感)
    for _ in range(10000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r, g, b, a = bg_color
        variation = random.randint(-10, 10)
        draw.point((x, y), fill=(max(0, min(255, r + variation)), 
                                 max(0, min(255, g + variation)), 
                                 max(0, min(255, b + variation)), 255))

    # 2. 绘制地貌色块 (街道与远景)
    # 远景：大相国寺轮廓 (深色剪影)
    temple_color = (47, 79, 79, 255) # DarkSlateGray
    draw.polygon([(200, 400), (300, 100), (400, 400)], fill=temple_color) # 塔尖1
    draw.polygon([(450, 350), (500, 150), (550, 350)], fill=temple_color) # 塔尖2
    draw.rectangle([100, 400, 700, 500], fill=temple_color) # 寺庙主体

    # 中景：街道 (灰色石板路)
    street_color = (80, 80, 80, 255)
    draw.rectangle([0, 600, 1920, 950], fill=street_color)
    # 街道纹理
    for i in range(0, 1920, 40):
        for j in range(600, 950, 40):
            if random.random() > 0.7:
                draw.rectangle([i, j, i+35, j+35], fill=(90, 90, 90, 255))

    # 3. 绘制网格线 (辅助线)
    grid_color = (255, 255, 255, 30)
    for x in range(0, width, cell_size):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, cell_size):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # 4. 元素清单
    elements = [
        {
            "name": "路边摊位",
            "type": "building",
            "rect": {"x": 200, "y": 700, "w": 150, "h": 120},
            "color": (210, 180, 140, 255) # Tan
        },
        {
            "name": "通缉告示榜",
            "type": "building",
            "rect": {"x": 800, "y": 650, "w": 100, "h": 150},
            "color": (160, 82, 45, 255) # Sienna
        },
        {
            "name": "勾栏瓦舍入口",
            "type": "building",
            "rect": {"x": 1400, "y": 500, "w": 300, "h": 400},
            "color": (178, 34, 34, 255) # Firebrick
        }
    ]

    # 尝试加载中文字体
    try:
        # 常见系统字体路径
        font_paths = [
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
            "/usr/share/fonts/winfonts/simhei.ttf"
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 24)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # 5. 遍历绘制元素
    for item in elements:
        r = item["rect"]
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]
        
        # 绘制建筑主体
        draw.rectangle([x, y, x + w, y + h], fill=item["color"], outline=(0, 0, 0, 255), width=3)
        
        # 绘制具象化屋顶 (如果是 building)
        if item["type"] == "building":
            draw.polygon([(x - 10, y), (x + w + 10, y), (x + w // 2, y - 40)], 
                         fill=(60, 60, 60, 255), outline=(0, 0, 0, 255))

        # 绘制标注文字
        text = item["name"]
        # 计算文字位置 (居中)
        text_x = x + w // 2
        text_y = y + h // 2
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font, anchor="mm")

    # 6. 装饰性边框
    draw.rectangle([0, 0, width-1, height-1], outline=(255, 215, 0, 150), width=10)

    # 保存图片
    image.save(output_path, "PNG")

def main():
    parser = argparse.ArgumentParser(description="生成东京汴梁闹市布局简图")
    parser.add_argument("--output", type=str, required=True, help="输出文件路径 (例如: layout.png)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子整数")
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    draw_layout_map(args.output, args.seed)

if __name__ == "__main__":
    main()