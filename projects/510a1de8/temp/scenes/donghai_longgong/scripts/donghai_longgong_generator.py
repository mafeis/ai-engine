import argparse
import random
from PIL import Image, ImageDraw, ImageFont

def layout_map(output_path, seed):
    """
    生成东海龙宫场景布局简图
    """
    # 设置随机种子
    random.seed(seed)

    # 基础参数
    width, height = 1920, 1920
    grid_rows, grid_cols = 15, 15
    cell_size = 128
    
    # 颜色定义 (RGBA)
    bg_color = (0, 0, 139, 255)          # 深蓝色背景 #00008B
    palace_zone_color = (30, 144, 255, 255) # 顶部水晶宫区域 (DodgerBlue)
    coral_zone_color = (0, 105, 148, 255)   # 中部珊瑚迷宫 (SeaBlue)
    seabed_zone_color = (25, 25, 112, 255)  # 底部海床 (MidnightBlue)
    grid_line_color = (255, 255, 255, 40)   # 半透明白色网格
    
    # 创建画布
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # 1. 绘制地貌区域 (Terrain Zones)
    # 顶部水晶宫区域 (0-600)
    draw.rectangle([0, 0, width, 600], fill=palace_zone_color)
    # 中部珊瑚迷宫 (600-1400)
    draw.rectangle([0, 600, width, 1400], fill=coral_zone_color)
    # 底部海床 (1400-1920)
    draw.rectangle([0, 1400, width, height], fill=seabed_zone_color)

    # 2. 绘制装饰性纹理 (增加专业感)
    # 在珊瑚区随机绘制一些小圆点模拟珊瑚群
    for _ in range(100):
        rx = random.randint(0, width)
        ry = random.randint(600, 1400)
        rs = random.randint(5, 15)
        draw.ellipse([rx, ry, rx+rs, ry+rs], fill=(255, 105, 180, 100)) # 粉色珊瑚点

    # 3. 绘制网格
    for i in range(grid_cols + 1):
        x = i * cell_size
        draw.line([(x, 0), (x, height)], fill=grid_line_color, width=1)
    for j in range(grid_rows + 1):
        y = j * cell_size
        draw.line([(0, y), (width, y)], fill=grid_line_color, width=1)

    # 4. 元素清单
    elements = [
        {
            "name": "水晶宫主殿",
            "type": "building",
            "rect": {"x": 960, "y": 300, "w": 1100, "h": 600},
            "color": (173, 216, 230, 200) # 淡蓝色半透明
        },
        {
            "name": "气泡珊瑚",
            "type": "platform",
            "rect": {"x": 200, "y": 1500, "w": 200, "h": 200},
            "color": (255, 192, 203, 220) # 粉色
        },
        {
            "name": "张口蚌壳",
            "type": "rock",
            "rect": {"x": 1600, "y": 1600, "w": 200, "h": 150},
            "color": (245, 245, 220, 220) # 米色
        },
        {
            "name": "发光海草",
            "type": "tree",
            "rect": {"x": 500, "y": 1700, "w": 100, "h": 300},
            "color": (50, 205, 50, 220)   # 荧光绿
        }
    ]

    # 尝试加载字体 (处理中文字体兼容性)
    try:
        # 尝试常见的中文字体路径
        font_paths = ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 
                      "C:\\Windows\\Fonts\\msyh.ttc", 
                      "/System/Library/Fonts/STHeiti Light.ttc"]
        font = None
        for path in font_paths:
            try:
                font = ImageFont.truetype(path, 36)
                break
            except:
                continue
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # 5. 遍历并绘制元素
    for el in elements:
        rect = el["rect"]
        # 计算左上角和右下角坐标 (x, y 为中心点)
        left = rect["x"] - rect["w"] // 2
        top = rect["y"] - rect["h"] // 2
        right = rect["x"] + rect["w"] // 2
        bottom = rect["y"] + rect["h"] // 2
        
        shape_rect = [left, top, right, bottom]
        
        # 根据类型绘制不同形状
        if el["type"] == "building":
            # 绘制主殿外轮廓
            draw.rectangle(shape_rect, fill=el["color"], outline=(255, 255, 255, 255), width=5)
            # 绘制内部“定海神针”示意
            draw.line([(rect["x"], top + 50), (rect["x"], bottom - 50)], fill=(255, 215, 0, 255), width=15)
        elif el["type"] == "platform":
            # 绘制圆形气泡珊瑚
            draw.ellipse(shape_rect, fill=el["color"], outline=(255, 255, 255, 255), width=3)
            # 绘制上方小气泡
            for i in range(3):
                bx = rect["x"] + random.randint(-50, 50)
                by = top - 40 - (i * 40)
                draw.ellipse([bx, by, bx+20, by+20], outline=(255, 255, 255, 150), width=2)
        elif el["type"] == "rock":
            # 绘制蚌壳 (半圆弧)
            draw.chord(shape_rect, start=0, end=180, fill=el["color"], outline=(100, 100, 100, 255))
            # 珍珠示意
            draw.ellipse([rect["x"]-15, rect["y"]-15, rect["x"]+15, rect["y"]+15], fill=(255, 255, 255, 255))
        elif el["type"] == "tree":
            # 绘制海草 (细长椭圆)
            draw.ellipse(shape_rect, fill=el["color"], outline=(173, 255, 47, 255), width=4)

        # 6. 绘制标注文字
        text_bbox = draw.textbbox((0, 0), el["name"], font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        draw.text((rect["x"] - text_w // 2, rect["y"] - text_h // 2), el["name"], fill=(255, 255, 255, 255), font=font)

    # 7. 添加图例标题
    title = "东海龙宫 - 场景布局简图 (Layout Map)"
    draw.text((50, 50), title, fill=(255, 255, 255, 255), font=font)
    
    # 保存图片
    img.save(output_path, "PNG")

def main():
    parser = argparse.ArgumentParser(description="生成东海龙宫场景布局简图")
    parser.param_groups = []
    parser.add_argument("--output", type=str, required=True, help="输出文件路径 (例如: layout.png)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    
    args = parser.parse_args()
    
    layout_map(args.output, args.seed)

if __name__ == "__main__":
    main()