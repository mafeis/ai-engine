import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def add_texture(img, intensity=15):
    """
    为图像的非透明区域添加像素级噪点纹理，提升高级像素风的质感。
    """
    width, height = img.size
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if a > 0:  # 只对非透明像素处理
                noise = random.randint(-intensity, intensity)
                new_r = max(0, min(255, r + noise))
                new_g = max(0, min(255, g + noise))
                new_b = max(0, min(255, b + noise))
                pixels[x, y] = (new_r, new_g, new_b, a)

def safe_rect(draw, coords, fill=None, outline=None):
    """
    安全绘制矩形，确保 x0 < x1 且 y0 < y1。
    """
    x0, y0, x1, y1 = coords
    draw.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill, outline=outline)

def safe_ellipse(draw, coords, fill=None, outline=None):
    """
    安全绘制椭圆，确保 x0 < x1 且 y0 < y1。
    """
    x0, y0, x1, y1 = coords
    draw.ellipse([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill, outline=outline)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)
    
    # 图像尺寸与基础设置
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. 算法级颜色生成 (基于种子)
    # 官服主色 (暗红色系)
    base_red = random.randint(100, 160)
    robe_color = (base_red, random.randint(0, 40), random.randint(0, 40), 255)
    robe_shadow = (base_red // 2, 0, 0, 255)
    robe_highlight = (min(255, base_red + 40), 40, 40, 255)
    
    # 皮肤色
    skin_base = (random.randint(230, 255), random.randint(190, 210), random.randint(150, 180), 255)
    
    # 帽子色 (黑色系)
    hat_color = (random.randint(10, 30), random.randint(10, 30), random.randint(10, 30), 255)
    
    # 锈长矛色
    rust_color = (random.randint(120, 160), random.randint(60, 80), random.randint(20, 40), 255)
    wood_color = (80, 50, 30, 255)

    # 2. 底层绘制：阴影层 (整体向右下偏移)
    shadow_offset = 2
    # 身体阴影
    safe_rect(draw, [20+shadow_offset, 30+shadow_offset, 44+shadow_offset, 60+shadow_offset], fill=(0, 0, 0, 80))
    # 头部阴影
    safe_ellipse(draw, [24+shadow_offset, 18+shadow_offset, 40+shadow_offset, 34+shadow_offset], fill=(0, 0, 0, 80))

    # 3. 中层绘制：主体形状
    # 绘制长矛 (在身体后方)
    spear_x = random.randint(10, 18)
    safe_rect(draw, [spear_x, 10, spear_x+2, 62], fill=wood_color) # 矛柄
    safe_rect(draw, [spear_x-2, 5, spear_x+4, 15], fill=rust_color) # 矛头

    # 绘制官服 (躯干)
    safe_rect(draw, [20, 32, 44, 58], fill=robe_color)
    # 宽袖子
    safe_rect(draw, [14, 35, 20, 50], fill=robe_color)
    safe_rect(draw, [44, 35, 50, 50], fill=robe_color)
    
    # 绘制头部
    safe_ellipse(draw, [24, 18, 40, 34], fill=skin_base)
    
    # 绘制歪斜的黑帽子
    tilt = random.randint(-4, 4)
    safe_rect(draw, [20+tilt, 10, 44+tilt, 20], fill=hat_color)
    safe_rect(draw, [28+tilt, 5, 36+tilt, 12], fill=hat_color) # 帽顶

    # 4. 顶层绘制：高光与猥琐表情细节
    # 眯眯眼 (两条细线)
    draw.line([27, 25, 31, 25], fill=(50, 30, 0, 255), width=1)
    draw.line([33, 25, 37, 25], fill=(50, 30, 0, 255), width=1)
    
    # 猥琐的嘴 (歪斜的小线段)
    draw.line([30, 29, 35, 30], fill=(100, 50, 50, 255), width=1)
    
    # 官服细节：补子 (胸前装饰)
    safe_rect(draw, [28, 38, 36, 46], fill=(random.randint(180, 220), 160, 50, 255))
    
    # 矛尖锈迹斑点
    for _ in range(5):
        rx = random.randint(spear_x-2, spear_x+3)
        ry = random.randint(5, 14)
        draw.point((rx, ry), fill=(80, 30, 0, 255))

    # 5. 纹理优化：添加表面噪点
    add_texture(img, intensity=12)

    # 6. 边缘高光 (手动增强像素感)
    draw.point((25, 19), fill=robe_highlight)
    draw.point((21, 33), fill=robe_highlight)
    draw.point((43, 33), fill=robe_highlight)

    # 保存结果
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()