import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def get_variant_color(hex_color, seed_val, variation=20):
    """根据种子对颜色进行微调，增加视觉多样性"""
    rgb = ImageColor.getrgb(hex_color)
    r = max(0, min(255, rgb[0] + random.randint(-variation, variation)))
    g = max(0, min(255, rgb[1] + random.randint(-variation, variation)))
    b = max(0, min(255, rgb[2] + random.randint(-variation, variation)))
    return (r, g, b, 255)

def safe_rect(draw, coords, fill=None, outline=None):
    """安全绘制矩形，确保 x0 < x1 且 y0 < y1"""
    x0, y0, x1, y1 = coords
    x_start, x_end = sorted([int(x0), int(x1)])
    y_start, y_end = sorted([int(y0), int(y1)])
    if x_start == x_end: x_end += 1
    if y_start == y_end: y_end += 1
    draw.rectangle([x_start, y_start, x_end, y_end], fill=fill, outline=outline)

def add_noise(draw, coords, base_color, intensity=0.1):
    """为指定区域添加像素级纹理噪点"""
    x0, y0, x1, y1 = [int(c) for c in coords]
    x_start, x_end = sorted([x0, x1])
    y_start, y_end = sorted([y0, y1])
    
    for x in range(x_start, x_end + 1):
        for y in range(y_start, y_end + 1):
            if random.random() < 0.3:
                factor = 1 + random.uniform(-intensity, intensity)
                r = max(0, min(255, int(base_color[0] * factor)))
                g = max(0, min(255, int(base_color[1] * factor)))
                b = max(0, min(255, int(base_color[2] * factor)))
                draw.point((x, y), fill=(r, g, b, 255))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    random.seed(args.seed)
    
    # 图像尺寸与基础设置
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. 定义调色板 (受种子影响)
    colors = {
        'hair': get_variant_color('#1A1A1A', args.seed),      # 黑色短发
        'skin': get_variant_color('#FFDBAC', args.seed),      # 肤色
        'inner_robe': get_variant_color('#F5F5DC', args.seed),# 米白色内穿
        'outer_vest': get_variant_color('#1A237E', args.seed),# 深蓝色短褐
        'belt': get_variant_color('#5D4037', args.seed),      # 棕色皮质腰带
        'pants': get_variant_color('#212121', args.seed),     # 黑色束腿裤
        'cyan_band': get_variant_color('#00CED1', args.seed), # 青色抹额
        'talisman': get_variant_color('#FFEB3B', args.seed),  # 黄色符纸
        'gold': get_variant_color('#FFD700', args.seed),      # 金色粒子
        'shadow': (0, 0, 0, 60)                               # 通用阴影
    }

    # 角色比例定义 (3.5头身)
    # 头: 14px, 躯干: 18px, 腿: 22px
    center_x = 32
    head_y = 8
    body_y = 22
    legs_y = 40

    # --- 第一层：底层阴影/轮廓 ---
    # 整体投影
    draw.ellipse([center_x-10, 58, center_x+10, 62], fill=(0, 0, 0, 40))

    # --- 第二层：主体形状 ---
    
    # 1. 腿部与裤子
    safe_rect(draw, [center_x-6, legs_y, center_x+6, legs_y+16], fill=colors['pants'])
    add_noise(draw, [center_x-6, legs_y, center_x+6, legs_y+16], colors['pants'])
    
    # 2. 躯干 (内穿米白 + 外罩深蓝)
    # 内穿长袍
    safe_rect(draw, [center_x-7, body_y, center_x+7, legs_y], fill=colors['inner_robe'])
    # 外罩无袖短褐
    safe_rect(draw, [center_x-8, body_y, center_x+8, body_y+14], fill=colors['outer_vest'])
    add_noise(draw, [center_x-8, body_y, center_x+8, body_y+14], colors['outer_vest'])
    
    # 3. 头部与面部
    safe_rect(draw, [center_x-6, head_y+2, center_x+6, head_y+14], fill=colors['skin'])
    # 头发
    safe_rect(draw, [center_x-7, head_y, center_x+7, head_y+6], fill=colors['hair'])
    # 小发髻
    safe_rect(draw, [center_x-2, head_y-3, center_x+2, head_y], fill=colors['hair'])
    
    # --- 第三层：细节与高光 ---
    
    # 青色抹额 (北斗七星)
    safe_rect(draw, [center_x-6, head_y+5, center_x+6, head_y+7], fill=colors['cyan_band'])
    # 抹额上的七星点 (简化为像素点)
    for i in range(4):
        draw.point((center_x-3+i*2, head_y+6), fill=(255, 255, 255, 200))

    # 腰带与天命星盘
    safe_rect(draw, [center_x-8, body_y+14, center_x+8, body_y+17], fill=colors['belt'])
    # 星盘 (圆形小挂件)
    draw.ellipse([center_x+3, body_y+15, center_x+7, body_y+19], fill=(200, 200, 200, 255), outline=colors['belt'])

    # 绑腿与黄色符纸
    safe_rect(draw, [center_x-6, legs_y+10, center_x-3, legs_y+14], fill=colors['talisman'])
    safe_rect(draw, [center_x+3, legs_y+10, center_x+6, legs_y+14], fill=colors['talisman'])
    
    # 草鞋
    safe_rect(draw, [center_x-7, legs_y+16, center_x-2, legs_y+18], fill=(188, 170, 128, 255))
    safe_rect(draw, [center_x+2, legs_y+16, center_x+7, legs_y+18], fill=(188, 170, 128, 255))

    # 金色像素粒子 (动态升起感)
    for _ in range(15):
        px = random.randint(center_x-15, center_x+15)
        py = random.randint(10, 55)
        p_size = random.randint(1, 2)
        alpha = random.randint(100, 255)
        c = list(colors['gold'])
        c[3] = alpha
        safe_rect(draw, [px, py, px+p_size, py+p_size], fill=tuple(c))

    # 脸部简单五官 (像素风)
    draw.point((center_x-2, head_y+10), fill=(60, 40, 40, 255)) # 左眼
    draw.point((center_x+2, head_y+10), fill=(60, 40, 40, 255)) # 右眼

    # 最终保存
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()