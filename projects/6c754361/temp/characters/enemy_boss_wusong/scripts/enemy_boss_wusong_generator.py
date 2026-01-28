import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def get_safe_coords(x0, y0, x1, y1):
    """确保坐标满足 x0 < x1 且 y0 < y1"""
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]

def add_noise(draw, coords, color, density=0.2):
    """为指定区域添加像素噪点以增强质感"""
    x0, y0, x1, y1 = coords
    for _ in range(int((x1 - x0) * (y1 - y0) * density)):
        nx = random.randint(x0, x1 - 1)
        ny = random.randint(y0, y1 - 1)
        draw.point((nx, ny), fill=color)

def draw_pixel_rect(draw, x0, y0, x1, y1, fill_color, outline_color=None):
    """绘制带边框的安全矩形"""
    coords = get_safe_coords(x0, y0, x1, y1)
    draw.rectangle(coords, fill=fill_color, outline=outline_color)
    return coords

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)
    
    # 基础参数
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. 算法生成调色板
    # 皮肤色：受邪气影响，偏灰、偏紫或偏暗
    skin_base_h = random.randint(0, 30) if random.random() > 0.5 else random.randint(260, 300)
    skin_main = ImageColor.getrgb(f"hsl({skin_base_h}, {random.randint(20, 50)}%, {random.randint(40, 60)}%)")
    skin_shadow = ImageColor.getrgb(f"hsl({skin_base_h}, {random.randint(30, 60)}%, {random.randint(20, 35)}%)")
    skin_highlight = ImageColor.getrgb(f"hsl({skin_base_h}, {random.randint(10, 40)}%, {random.randint(70, 85)}%)")
    
    # 邪气/火焰色
    fire_color = ImageColor.getrgb(f"hsl({random.randint(270, 310)}, 90%, 60%)")
    fire_core = (255, 255, 255, 255)
    
    # 戒刀色
    blade_color = (30, 30, 35, 255)
    aura_color = (10, 0, 20, 180)

    # 2. 绘制底层：阴影与轮廓 (Shadow Layer)
    # 躯干阴影
    draw_pixel_rect(draw, 20, 20, 44, 55, skin_shadow)
    # 手臂阴影
    draw_pixel_rect(draw, 10, 25, 20, 45, skin_shadow)
    draw_pixel_rect(draw, 44, 25, 54, 45, skin_shadow)

    # 3. 绘制中层：主体形状 (Main Body Layer)
    # 躯干 (胸肌与腹肌区域)
    body_coords = draw_pixel_rect(draw, 22, 22, 42, 50, skin_main)
    # 肌肉线条绘制 (像素风模拟)
    # 胸肌
    draw_pixel_rect(draw, 24, 28, 31, 34, skin_shadow)
    draw_pixel_rect(draw, 33, 28, 40, 34, skin_shadow)
    # 腹肌 (六块肌)
    for i in range(3):
        draw_pixel_rect(draw, 26, 38 + i*4, 31, 40 + i*4, skin_shadow)
        draw_pixel_rect(draw, 33, 38 + i*4, 38, 40 + i*4, skin_shadow)
    
    # 头部
    head_coords = draw_pixel_rect(draw, 26, 10, 38, 22, skin_main)
    
    # 猛虎纹身 (算法生成随机纹理)
    tattoo_color = (10, 10, 20, 200)
    for _ in range(15):
        tx = random.randint(24, 40)
        ty = random.randint(25, 45)
        draw.point((tx, ty), fill=tattoo_color)
        if random.random() > 0.5:
            draw.point((tx+1, ty), fill=tattoo_color)

    # 4. 绘制顶层：武器与特效 (Highlight & Detail Layer)
    # 黑气戒刀 (左)
    draw_pixel_rect(draw, 5, 30, 12, 55, blade_color)
    draw_pixel_rect(draw, 5, 50, 15, 58, blade_color) # 刀尖
    # 黑气戒刀 (右)
    draw_pixel_rect(draw, 52, 30, 59, 55, blade_color)
    draw_pixel_rect(draw, 49, 50, 59, 58, blade_color) # 刀尖
    
    # 武器黑气 (Aura)
    for _ in range(40):
        ax = random.choice([random.randint(3, 14), random.randint(50, 61)])
        ay = random.randint(25, 60)
        draw.point((ax, ay), fill=aura_color)

    # 双眼紫火
    eye_y = 15
    # 左眼
    draw.point((29, eye_y), fill=fire_core)
    for _ in range(10):
        fx, fy = 29 + random.randint(-2, 2), eye_y - random.randint(1, 6)
        draw.point((fx, fy), fill=fire_color)
    # 右眼
    draw.point((35, eye_y), fill=fire_core)
    for _ in range(10):
        fx, fy = 35 + random.randint(-2, 2), eye_y - random.randint(1, 6)
        draw.point((fx, fy), fill=fire_color)

    # 5. 纹理优化 (Texture Noise)
    # 为皮肤添加高光和噪点
    add_noise(draw, body_coords, skin_highlight, density=0.15)
    add_noise(draw, head_coords, skin_highlight, density=0.1)
    
    # 肌肉边缘高光
    draw.point((23, 23), fill=skin_highlight)
    draw.point((41, 23), fill=skin_highlight)
    draw.point((23, 37), fill=skin_highlight)
    draw.point((41, 37), fill=skin_highlight)

    # 6. 最终细节：邪气侵蚀的边缘
    for _ in range(20):
        ex = random.randint(20, 44)
        ey = random.randint(10, 55)
        if random.random() > 0.7:
            draw.point((ex, ey), fill=fire_color)

    # 保存图像
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()