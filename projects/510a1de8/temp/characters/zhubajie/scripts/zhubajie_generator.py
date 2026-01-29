import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def safe_coords(x0, y0, x1, y1):
    """确保坐标满足 x0 < x1 且 y0 < y1"""
    nx0, nx1 = (x0, x1) if x0 < x1 else (x1, x0)
    ny0, ny1 = (y0, y1) if y0 < y1 else (y1, y0)
    if nx0 == nx1: nx1 += 1
    if ny0 == ny1: ny1 += 1
    return [nx0, ny0, nx1, ny1]

def add_texture(img, intensity=15):
    """为图像添加像素级纹理噪声"""
    pixels = img.load()
    width, height = img.size
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if a > 0:  # 只处理非透明像素
                noise = random.randint(-intensity, intensity)
                pixels[x, y] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise)),
                    a
                )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 创建 64x64 透明画布
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 随机颜色方案
    pig_skin = (random.randint(240, 255), random.randint(180, 200), random.randint(180, 210), 255)
    pig_skin_dark = (pig_skin[0]-30, pig_skin[1]-30, pig_skin[2]-30, 255)
    robe_color = (random.randint(20, 40), random.randint(20, 40), random.randint(20, 40), 255)
    melon_green = (random.randint(30, 60), random.randint(120, 160), random.randint(30, 60), 255)
    melon_stripe = (random.randint(10, 30), random.randint(60, 90), random.randint(10, 30), 255)
    rake_wood = (random.randint(100, 140), random.randint(60, 80), random.randint(30, 50), 255)

    # 1. 绘制投影 (Shadow)
    draw.ellipse(safe_coords(10, 50, 54, 60), fill=(0, 0, 0, 60))

    # 2. 绘制大西瓜 (Watermelon)
    # 西瓜主体
    draw.ellipse(safe_coords(8, 35, 56, 58), fill=melon_green, outline=melon_stripe, width=1)
    # 西瓜条纹
    for i in range(12, 56, 8):
        draw.arc(safe_coords(i, 35, i+4, 58), start=0, end=180, fill=melon_stripe, width=1)

    # 3. 绘制猪人身体 (Pig Body - Lying)
    # 身体躯干
    draw.ellipse(safe_coords(15, 25, 45, 48), fill=pig_skin)
    
    # 4. 黑色僧袍 (Monk Robe)
    # 覆盖在身体上的宽松袍子
    draw.chord(safe_coords(14, 26, 46, 50), start=0, end=180, fill=robe_color)
    draw.rectangle(safe_coords(18, 30, 42, 45), fill=robe_color)

    # 5. 猪头 (Pig Head)
    head_x = 38 + random.randint(-2, 2)
    head_y = 18 + random.randint(-2, 2)
    draw.ellipse(safe_coords(head_x, head_y, head_x+18, head_y+18), fill=pig_skin)
    
    # 猪耳朵
    draw.ellipse(safe_coords(head_x-2, head_y+2, head_x+4, head_y+8), fill=pig_skin_dark)
    draw.ellipse(safe_coords(head_x+14, head_y+2, head_x+20, head_y+8), fill=pig_skin_dark)

    # 猪鼻子 (Snout)
    draw.ellipse(safe_coords(head_x+5, head_y+10, head_x+13, head_y+16), fill=pig_skin_dark)
    # 鼻孔
    draw.point([(head_x+7, head_y+13), (head_x+11, head_y+13)], fill=(80, 40, 40, 255))

    # 睡眼 (Sleepy Eyes)
    draw.line(safe_coords(head_x+4, head_y+8, head_x+8, head_y+8), fill=(0, 0, 0, 255), width=1)
    draw.line(safe_coords(head_x+10, head_y+8, head_x+14, head_y+8), fill=(0, 0, 0, 255), width=1)

    # 6. 木耙子 (Wooden Rake as back-scratcher)
    # 耙柄
    rake_handle_x = 12
    rake_handle_y = 15
    draw.line([rake_handle_x, rake_handle_y, 35, 35], fill=rake_wood, width=2)
    # 耙齿 (Rake head)
    rake_head_x, rake_head_y = 12, 15
    for i in range(-4, 5, 2):
        draw.line([rake_head_x + i, rake_head_y - 2, rake_head_x + i, rake_head_y + 2], fill=rake_wood, width=1)

    # 7. 手臂 (Arms)
    # 抱着耙子的手
    draw.ellipse(safe_coords(25, 32, 32, 38), fill=pig_skin)

    # 8. 细节与纹理 (Texture Noise)
    add_texture(img, intensity=12)

    # 保存图像
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()