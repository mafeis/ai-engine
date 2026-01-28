import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def add_texture(img, intensity=20):
    """
    为图像的有色区域添加像素级噪点纹理，提升像素风的质感。
    """
    pixels = img.load()
    width, height = img.size
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if a > 0:  # 只对非透明区域添加噪点
                noise = random.randint(-intensity, intensity)
                new_r = max(0, min(255, r + noise))
                new_g = max(0, min(255, g + noise))
                new_b = max(0, min(255, b + noise))
                pixels[x, y] = (new_r, new_g, new_b, a)

def safe_rect(draw, coords, fill=None, outline=None):
    """
    安全绘制矩形，确保 x0 < x1 且 y0 < y1，防止坐标错误。
    """
    x0, y0, x1, y1 = coords
    draw.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill, outline=outline)

def safe_ellipse(draw, coords, fill=None, outline=None):
    """
    安全绘制椭圆。
    """
    x0, y0, x1, y1 = coords
    draw.ellipse([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill, outline=outline)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    random.seed(args.seed)
    
    # 基础参数
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. 调色板生成 (受种子影响)
    hue_shift = random.randint(-20, 20)
    
    # 张青色调 (偏暗、粗犷)
    zq_skin = (200 + hue_shift, 160 + hue_shift, 130)
    zq_apron = (60 + random.randint(-10, 10), 55, 50)
    zq_hair = (40, 35, 30)
    
    # 孙二娘色调 (明亮、红色系)
    sn_skin = (245, 210 + hue_shift, 190)
    sn_red = (200 + random.randint(0, 55), 30, 40)
    sn_hair = (30, 25, 25)
    
    metal_color = (160, 165, 175)
    shadow_color = (0, 0, 0, 80)

    # --- 绘制张青 (左侧) ---
    # 底层阴影
    safe_rect(draw, [12, 17, 32, 57], fill=shadow_color)
    
    # 主体：身体与头部
    safe_rect(draw, [15, 15, 27, 25], fill=zq_skin) # 头部
    safe_rect(draw, [13, 25, 29, 55], fill=(80, 70, 60)) # 身体
    
    # 细节：粗犷发型与胡须
    safe_rect(draw, [15, 13, 27, 17], fill=zq_hair) # 头发
    safe_rect(draw, [18, 23, 24, 27], fill=zq_hair) # 胡须
    
    # 围裙 (油腻感)
    safe_rect(draw, [14, 30, 28, 52], fill=zq_apron)
    # 围裙上的污渍
    for _ in range(5):
        sx = random.randint(15, 26)
        sy = random.randint(32, 50)
        safe_rect(draw, [sx, sy, sx+2, sy+1], fill=(40, 30, 20))
        
    # 菜刀
    safe_rect(draw, [6, 35, 14, 45], fill=metal_color, outline=(50, 50, 50)) # 刀刃
    safe_rect(draw, [14, 38, 17, 41], fill=(100, 70, 50)) # 刀柄

    # --- 绘制孙二娘 (右侧) ---
    # 底层阴影
    safe_rect(draw, [36, 17, 54, 57], fill=shadow_color)
    
    # 主体：头部与身体
    safe_rect(draw, [38, 15, 48, 25], fill=sn_skin) # 头部
    safe_rect(draw, [36, 25, 50, 55], fill=sn_skin) # 身体
    
    # 红色抹胸
    safe_rect(draw, [36, 28, 50, 38], fill=sn_red)
    
    # 发间大红花
    flower_x, flower_y = 46, 12
    safe_ellipse(draw, [flower_x, flower_y, flower_x+6, flower_y+6], fill=(255, 50, 50))
    safe_ellipse(draw, [flower_x+2, flower_y+2, flower_x+4, flower_y+4], fill=(255, 200, 0)) # 花蕊
    
    # 头发
    safe_rect(draw, [38, 13, 48, 18], fill=sn_hair)
    
    # 腰间双短刀
    # 左短刀
    safe_rect(draw, [33, 40, 36, 50], fill=metal_color, outline=(60, 60, 60))
    # 右短刀
    safe_rect(draw, [50, 40, 53, 50], fill=metal_color, outline=(60, 60, 60))

    # 3. 顶层高光与边缘细节
    # 张青眼睛
    draw.point([(19, 19), (23, 19)], fill=(0, 0, 0))
    # 孙二娘眼睛
    draw.point([(41, 19), (45, 19)], fill=(0, 0, 0))
    
    # 刀刃高光
    draw.line([(7, 36), (13, 36)], fill=(255, 255, 255, 150))
    draw.line([(34, 41), (34, 48)], fill=(255, 255, 255, 150))
    draw.line([(51, 41), (51, 48)], fill=(255, 255, 255, 150))

    # 4. 添加表面纹理 (算法级优化)
    add_texture(img, intensity=15 + (args.seed % 10))

    # 5. 最终保存
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()