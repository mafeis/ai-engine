import argparse
import random
from PIL import Image, ImageDraw, ImageFont

def draw_layout_map(output_path, seed):
    # 设置随机种子
    random.seed(seed)
    
    # 基础参数
    width, height = 2560, 1440
    bg_color = "#FFFACD"  # 柠檬绸色
    grid_rows, grid_cols = 12, 20
    cell_size = 128
    
    # 创建画布 (RGBA)
    image = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 1. 绘制背景地貌
    # 背景区 (0-400): 仙境天空
    draw.rectangle([0, 0, width, 400], fill="#87CEEB") # 天蓝色
    
    # 绘制背景仙岛 (随机生成几个)
    for _ in range(5):
        ix = random.randint(100, width - 100)
        iy = random.randint(50, 300)
        iw = random.randint(200, 400)
        ih = random.randint(100, 200)
        draw.ellipse([ix-iw//2, iy-ih//2, ix+iw//2, iy+ih//2], fill="#98FB98", outline="#2E8B57", width=3)
    
    # 绘制彩虹桥 (示意)
    draw.arc([200, 50, 2360, 600], start=180, end=0, fill="#FF69B4", width=10)
    
    # 中场 (400-1000): 汉白玉阶梯
    # 用渐变色块模拟阶梯感
    for i in range(400, 1000, 40):
        shade = 240 - (i - 400) // 10
        color = (shade, shade, shade)
        draw.rectangle([0, i, width, i + 40], fill=color, outline="#DCDCDC")

    # 前庭 (1000-1440): 白色方砖广场
    draw.rectangle([0, 1000, width, 1440], fill="#FFFFFF")
    # 绘制方砖纹理
    for x in range(0, width, 100):
        draw.line([x, 1000, x, 1440], fill="#E0E0E0", width=1)
    for y in range(1000, 1440, 100):
        draw.line([0, y, width, y], fill="#E0E0E0", width=1)

    # 2. 绘制网格辅助线 (半透明)
    grid_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid_overlay)
    for r in range(grid_rows + 1):
        y = r * cell_size
        grid_draw.line([0, y, width, y], fill=(100, 100, 100, 50), width=1)
    for c in range(grid_cols + 1):
        x = c * cell_size
        grid_draw.line([x, 0, x, height], fill=(100, 100, 100, 50), width=1)
    image = Image.alpha_composite(image, grid_overlay)
    draw = ImageDraw.Draw(image)

    # 3. 绘制元素清单
    elements = [
        {
            "name": "南天门牌坊",
            "type": "building",
            "rect": {"x": 1280, "y": 400, "w": 800, "h": 800},
            "color": "#F5F5F5",
            "border": "#FFD700"
        },
        {
            "name": "萌感石狮子",
            "type": "rock",
            "rect": {"x": 1000, "y": 900, "w": 300, "h": 300},
            "color": "#B0C4DE",
            "border": "#708090"
        },
        {
            "name": "长明灯座",
            "type": "building",
            "rect": {"x": 400, "y": 1100, "w": 100, "h": 200},
            "color": "#FFF8DC",
            "border": "#DAA520"
        },
        {
            "name": "动态流云层",
            "type": "water",
            "rect": {"x": 1280, "y": 1400, "w": 2560, "h": 50},
            "color": (255, 255, 255, 180),
            "border": "#AFEEEE"
        }
    ]

    # 尝试加载字体
    try:
        font = ImageFont.truetype("Arial Unicode.ttf", 40)
    except:
        font = ImageFont.load_default()

    for item in elements:
        rect = item["rect"]
        # 计算左上角坐标 (假设输入 x, y 为中心点)
        x1 = rect["x"] - rect["w"] // 2
        y1 = rect["y"] - rect["h"] // 2
        x2 = rect["x"] + rect["w"] // 2
        y2 = rect["y"] + rect["h"] // 2
        
        # 根据类型绘制不同形状
        if item["type"] == "building":
            # 绘制主体
            draw.rectangle([x1, y1, x2, y2], fill=item["color"], outline=item["border"], width=5)
            # 绘制屋顶装饰 (Q版三角形)
            draw.polygon([(x1, y1), (x2, y1), (rect["x"], y1 - 100)], fill=item["border"])
        elif item["type"] == "rock":
            # 绘制圆润的石狮子占位
            draw.ellipse([x1, y1, x2, y2], fill=item["color"], outline=item["border"], width=4)
        elif item["type"] == "water":
            # 绘制半透明云雾
            draw.rounded_rectangle([x1, y1, x2, y2], radius=20, fill=item["color"], outline=item["border"])

        # 绘制标注文字
        text_pos = (rect["x"], rect["y"])
        draw.text(text_pos, item["name"], fill="#000000", font=font, anchor="mm")

    # 额外绘制对称的灯座和狮子以丰富布局
    # 对称狮子
    draw.ellipse([1560-150, 900-150, 1560+150, 900+150], fill="#B0C4DE", outline="#708090", width=4)
    draw.text((1560, 900), "萌感石狮子", fill="#000000", font=font, anchor="mm")
    
    # 绘制其余7个灯座 (分布在广场边缘)
    lamp_positions = [(400, 1100), (700, 1100), (1000, 1100), (1300, 1100), 
                      (1600, 1100), (1900, 1100), (2200, 1100), (2500, 1100)]
    for pos in lamp_positions:
        lx, ly = pos
        draw.rectangle([lx-50, ly-100, lx+50, ly+100], fill="#FFF8DC", outline="#DAA520", width=2)

    # 保存结果
    image.save(output_path)

def main():
    parser = argparse.ArgumentParser(description="生成南天门场景布局简图")
    parser.param = parser.add_argument("--output", type=str, required=True, help="输出文件路径 (e.g. layout.png)")
    parser.param = parser.add_argument("--seed", type=int, default=42, help="随机种子")
    
    args = parser.parse_args()
    
    draw_layout_map(args.output, args.seed)

if __name__ == "__main__":
    main()