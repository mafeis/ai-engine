import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def add_noise(draw, x0, y0, x1, y1, base_color, intensity=0.1):
    """
    为指定区域添加纹理噪点，模拟高级像素风的质感。
    """
    x0, x1 = sorted([int(x0), int(x1)])
    y0, y1 = sorted([int(y0), int(y1)])
    
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if random.random() < 0.3:  # 噪点密度
                # 随机调整颜色的亮度
                factor = 1 + random.uniform(-intensity, intensity)
                r = max(0, min(255, int(base_color[0] * factor)))
                g = max(0, min(255, int(base_color[1] * factor)))
                b = max(0, min(255, int(base_color[2] * factor)))
                a = base_color[3] if len(base_color) > 3 else 255
                draw.point((x, y), fill=(r, g, b, a))

def safe_draw_rect(draw, coords, fill=None, outline=None, width=1):
    """
    安全绘制矩形，确保 x0 < x1 且 y0 < y1。
    """
    x0, y0, x1, y1 = coords
    nx0, nx1 = sorted([x0, x1])
    ny0, ny1 = sorted([y0, y1])
    draw.rectangle([nx0, ny0, nx1, ny1], fill=fill, outline=outline, width=width)

def safe_draw_ellipse(draw, coords, fill=None, outline=None, width=1):
    """
    安全绘制椭圆，确保 x0 < x1 且 y0 < y1。
    """
    x0, y0, x1, y1 = coords
    nx0, nx1 = sorted([x0, x1])
    ny0, ny1 = sorted([y0, y1])
    draw.ellipse([nx0, ny0, nx1, ny1], fill=fill, outline=outline, width=width)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)
    
    # 图像尺寸 64x64
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. 确定调色板 (基于种子生成不同的青铜色调)
    hue_shift = random.randint(-20, 20)
    base_bronze = (150 + hue_shift, 100 + hue_shift // 2, 50, 255)
    dark_bronze = (80 + hue_shift, 50 + hue_shift // 2, 20, 255)
    light_bronze = (210 + hue_shift, 160 + hue_shift // 2, 80, 255)
    glow_red = (255, 0, 0, 255)
    shadow_color = (20, 10, 5, 150)

    # 2. 绘制底层阴影/轮廓 (Layer 1)
    # 身体大轮廓阴影
    safe_draw_rect(draw, [12, 18, 52, 58], fill=shadow_color)
    # 武器阴影
    safe_draw_ellipse(draw, [42, 22, 62, 42], fill=shadow_color)

    # 3. 绘制主体形状 (Layer 2)
    # 腿部 (厚重)
    safe_draw_rect(draw, [18, 45, 30, 60], fill=dark_bronze)
    safe_draw_rect(draw, [34, 45, 46, 60], fill=dark_bronze)
    
    # 躯干 (巨大)
    safe_draw_rect(draw, [14, 20, 50, 48], fill=base_bronze)
    
    # 肩甲 (Pauldrons)
    safe_draw_ellipse(draw, [10, 18, 28, 35], fill=base_bronze)
    safe_draw_ellipse(draw, [36, 18, 54, 35], fill=base_bronze)
    
    # 头盔
    safe_draw_rect(draw, [24, 8, 40, 24], fill=base_bronze)
    # 头盔缝隙 (黑色)
    safe_draw_rect(draw, [26, 16, 38, 19], fill=(20, 20, 20, 255))
    
    # 手持流星锤 (柄与链)
    draw.line([45, 40, 52, 32], fill=(100, 100, 100, 255), width=2)
    # 流星锤球体
    safe_draw_ellipse(draw, [44, 20, 60, 36], fill=dark_bronze)

    # 4. 绘制高光与细节 (Layer 3)
    # 红色凶光
    draw.point([(30, 17), (34, 17)], fill=glow_red)
    
    # 盔甲边缘高光
    draw.line([15, 21, 49, 21], fill=light_bronze, width=1) # 胸甲上沿
    draw.line([25, 9, 39, 9], fill=light_bronze, width=1)   # 头盔顶
    
    # 流星锤尖刺
    spikes = [(52, 18), (62, 28), (52, 38), (42, 28), (58, 22), (46, 22)]
    for sx, sy in spikes:
        draw.point((sx, sy), fill=light_bronze)

    # 5. 添加表面纹理 (Texture Noise)
    # 为盔甲各部分添加噪点
    add_noise(draw, 14, 20, 50, 48, base_bronze, 0.15) # 躯干
    add_noise(draw, 24, 8, 40, 24, base_bronze, 0.1)  # 头盔
    add_noise(draw, 44, 20, 60, 36, dark_bronze, 0.2) # 武器

    # 6. 像素风增强：强制一些边缘锯齿感 (可选)
    # 通过在边缘随机点缀深色像素实现
    for _ in range(40):
        rx = random.randint(14, 50)
        ry = random.randint(20, 60)
        if img.getpixel((rx, ry))[3] > 0:
            draw.point((rx, ry), fill=(0, 0, 0, 40))

    # 保存图像
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()