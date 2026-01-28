import argparse
import random
from PIL import Image, ImageDraw, ImageFont

def main():
    # 1. 脚本接口: 接受 --output 和 --seed 参数
    parser = argparse.ArgumentParser(description="生成沧州·风雪山神庙场景布局简图")
    parser.add_argument("--output", type=str, required=True, help="输出图像的路径")
    parser.add_argument("--seed", type=int, required=True, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 2. 场景基本信息
    width, height = 960, 540
    background_color = "#E0FFFF"  # 极淡的青色，模拟雪地背景
    grid_info = {'rows': 9, 'cols': 16, 'cell_size': 60}
    
    elements = [
        {
            "name": "山神塑像",
            "type": "building",
            "rect": {"x": 400, "y": 100, "w": 160, "h": 250},
            "color": "#4A4A4A", # 深灰色
            "description": "面目狰狞的旧塑像"
        },
        {
            "name": "破碎的窗户",
            "type": "platform",
            "rect": {"x": 100, "y": 150, "w": 80, "h": 120},
            "color": "#ADD8E6", # 淡蓝色
            "description": "寒风与雪花从此灌入"
        },
        {
            "name": "雪地血迹",
            "type": "water",
            "rect": {"x": 600, "y": 450, "w": 200, "h": 50},
            "color": "#8B0000", # 深红色
            "description": "纯白积雪上触目惊心的鲜红"
        }
    ]

    # 创建 RGBA 图像
    image = Image.new("RGBA", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # 3. 绘制核心 (layout_map)
    
    # --- 绘制地貌与环境纹理 ---
    # 绘制厚积雪的纹理（随机分布的浅蓝色/白色像素点）
    for _ in range(2000):
        sx = random.randint(0, width)
        sy = random.randint(0, height)
        snow_color = random.choice(["#FFFFFF", "#F0FFFF", "#D1EEEE"])
        draw.point((sx, sy), fill=snow_color)

    # 绘制山庙室内区域（深色地砖感）
    temple_floor = [200, 80, 760, 400] # 粗略定义室内范围
    draw.rectangle(temple_floor, fill=(60, 60, 80, 100), outline="#2F4F4F", width=2)

    # --- 绘制网格 (辅助线) ---
    for i in range(grid_info['cols'] + 1):
        x = i * grid_info['cell_size']
        draw.line([(x, 0), (x, height)], fill=(200, 200, 200, 50), width=1)
    for j in range(grid_info['rows'] + 1):
        y = j * grid_info['cell_size']
        draw.line([(0, y), (width, y)], fill=(200, 200, 200, 50), width=1)

    # --- 遍历绘制元素清单 ---
    try:
        # 尝试加载中文字体，若失败则使用默认
        font = ImageFont.truetype("SimHei.ttf", 16)
    except:
        font = ImageFont.load_default()

    for item in elements:
        rect = item['rect']
        x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
        shape_rect = [x, y, x + w, y + h]

        if item['type'] == 'building':
            # 绘制山神像：主体矩形 + 顶部三角形（简易外轮廓）
            draw.rectangle(shape_rect, fill=item['color'], outline="#000000", width=2)
            draw.polygon([(x, y), (x + w // 2, y - 40), (x + w, y)], fill="#2F4F4F", outline="#000000")
        
        elif item['type'] == 'platform':
            # 绘制窗户：带边框的半透明色块
            draw.rectangle(shape_rect, fill=(173, 216, 230, 180), outline="#4682B4", width=3)
            # 增加破碎线条
            draw.line([x, y, x + w, y + h], fill="#F0F8FF", width=1)
            draw.line([x + w, y, x, y + h], fill="#F0F8FF", width=1)

        elif item['type'] == 'water':
            # 绘制血迹：不规则色块（用多个椭圆叠加模拟）
            for _ in range(5):
                rx = random.randint(x, x + w - 20)
                ry = random.randint(y, y + h - 10)
                draw.ellipse([rx, ry, rx + 40, ry + 20], fill=item['color'])

        # 标注名称
        text_pos = (x + w // 2 - 20, y + h // 2 - 10)
        # 绘制文字背景，增加可读性
        text_bbox = draw.textbbox(text_pos, item['name'], font=font)
        draw.rectangle(text_bbox, fill=(255, 255, 255, 150))
        draw.text(text_pos, item['name'], fill="#000000", font=font)

    # --- 增加动态粒子流视觉表现 (风雪) ---
    for _ in range(100):
        lx = random.randint(0, width)
        ly = random.randint(0, height)
        length = random.randint(20, 60)
        # 倾斜的线条模拟狂风
        draw.line([lx, ly, lx + length, ly + length // 3], fill=(255, 255, 255, 180), width=1)

    # 4. 输出保存
    image.save(args.output, "PNG")

if __name__ == "__main__":
    main()