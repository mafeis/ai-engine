import argparse
import random
from PIL import Image, ImageDraw, ImageFont

def main():
    # 配置命令行参数解析
    parser = argparse.ArgumentParser(description="生成浔阳楼·酒肆场景布局简图")
    parser.add_argument("--output", type=str, required=True, help="输出图像的路径")
    parser.add_argument("--seed", type=int, required=True, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子以确保可复现性
    random.seed(args.seed)

    # 场景基础信息
    width, height = 640, 480
    background_color = "#DEB887"  # 实木色底色
    grid_rows, grid_cols = 6, 8
    cell_size = 80

    # 元素清单
    elements = [
        {
            "name": "临江酒桌",
            "type": "platform",
            "rect": {"x": 50, "y": 300, "w": 120, "h": 80},
            "color": "#8B4513",  # 深褐色
            "description": "摆放着精致酒具的木桌"
        },
        {
            "name": "题壁诗墙",
            "type": "building",
            "rect": {"x": 400, "y": 100, "w": 200, "h": 150},
            "color": "#F5F5DC",  # 米白色（纸张感）
            "description": "写满诗词的墙壁"
        }
    ]

    # 创建 RGBA 图像
    image = Image.new("RGBA", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # 1. 绘制背景纹理（模拟木质地板）
    for y in range(0, height, 4):
        line_color = (210, 180, 140, 255) if (y // 4) % 2 == 0 else (222, 184, 135, 255)
        draw.line([(0, y), (width, y)], fill=line_color, width=2)

    # 2. 绘制地貌绘制：浔阳江景 (River/Water)
    # 根据描述“窗外可见浔阳江景”，在顶部绘制一个蓝色区域代表窗外景观
    river_color = (100, 149, 237, 200)  # 矢车菊蓝
    draw.rectangle([0, 0, width, 60], fill=river_color)
    # 绘制简单的波浪纹理
    for i in range(0, width, 20):
        draw.arc([i, 20, i + 20, 40], start=0, end=180, fill=(255, 255, 255, 100))

    # 3. 绘制网格线 (Grid)
    grid_line_color = (0, 0, 0, 40)
    for r in range(grid_rows + 1):
        draw.line([(0, r * cell_size), (width, r * cell_size)], fill=grid_line_color, width=1)
    for c in range(grid_cols + 1):
        draw.line([(c * cell_size, 0), (c * cell_size, height)], fill=grid_line_color, width=1)

    # 4. 遍历并绘制元素
    try:
        # 尝试加载中文字体，若失败则使用默认字体
        font = ImageFont.truetype("SimHei.ttf", 16)
    except:
        font = ImageFont.load_default()

    for item in elements:
        rect = item["rect"]
        x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]
        shape_color = item["color"]
        
        if item["type"] == "building":
            # 绘制带边框的建筑（诗墙）
            draw.rectangle([x, y, x + w, y + h], fill=shape_color, outline="#5D4037", width=3)
            # 增加一些装饰线模拟诗词行
            for line_y in range(y + 20, y + h - 10, 20):
                draw.line([(x + 20, line_y), (x + w - 20, line_y)], fill="#A9A9A9", width=1)
        
        elif item["type"] == "platform":
            # 绘制平台（酒桌）
            draw.rectangle([x, y, x + w, y + h], fill=shape_color, outline="#3E2723", width=2)
            # 绘制桌腿阴影感
            draw.rectangle([x + 5, y + h, x + 15, y + h + 10], fill="#3E2723")
            draw.rectangle([x + w - 15, y + h, x + w - 5, y + h + 10], fill="#3E2723")

        # 5. 标注名称
        text_content = item["name"]
        # 计算文字位置（居中）
        text_x = x + (w // 2) - 20
        text_y = y + (h // 2) - 10
        # 绘制文字背景阴影
        draw.text((text_x + 1, text_y + 1), text_content, fill="black", font=font)
        draw.text((text_x, text_y), text_content, fill="white", font=font)

    # 6. 绘制整体边框（设计草图感）
    draw.rectangle([0, 0, width - 1, height - 1], outline="#5D4037", width=5)

    # 7. 添加场景标题
    title = "场景布局: 浔阳楼·酒肆 (640x480)"
    draw.text((20, height - 30), title, fill="#3E2723", font=font)

    # 保存图像
    image.save(args.output)

if __name__ == "__main__":
    main()