import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def add_texture_noise(img, intensity=15):
    """
    为图像中非透明区域添加像素级纹理噪声，增加质感。
    """
    width, height = img.size
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # 随机产生颜色偏移
                noise = random.randint(-intensity, intensity)
                r = max(0, min(255, r + noise))
                g = max(0, min(255, g + noise))
                b = max(0, min(255, b + noise))
                pixels[x, y] = (r, g, b, a)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 图像尺寸 64x64，RGBA模式（透明背景）
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # --- 随机参数生成 ---
    # 漂浮偏移量
    y_off = random.randint(-4, 2)
    # 汉服紫色调随机
    p_r = random.randint(130, 180)
    p_g = random.randint(100, 150)
    p_b = random.randint(200, 255)
    purple_color = (p_r, p_g, p_b, 255)
    white_color = (245, 245, 255, 255)
    skin_color = (255, 224, 200, 255)
    hair_color = (20, 20, 25, 255)
    jade_color = (100, 255, 180, 255)
    aura_color = (220, 220, 255, 60)

    # --- 1. 绘制光晕 (Aura) ---
    aura_size = random.randint(22, 28)
    for i in range(3):
        r_val = aura_size + i * 4
        draw.ellipse([32 - r_val, 32 + y_off - r_val, 32 + r_val, 32 + y_off + r_val], 
                     fill=(p_r, p_g, p_b, 40 - i * 10))

    # --- 2. 绘制投影 (底部微弱阴影) ---
    draw.ellipse([20, 58, 44, 62], fill=(0, 0, 0, 40))

    # --- 3. 绘制后发 (Back Hair) ---
    hair_w = random.randint(16, 22)
    draw.ellipse([32 - hair_w, 15 + y_off, 32 + hair_w, 55 + y_off], fill=hair_color)

    # --- 4. 绘制汉服 (Hanfu - Flowing Sleeves & Body) ---
    # 身体/裙摆
    draw.polygon([(22, 35 + y_off), (42, 35 + y_off), (48, 58 + y_off), (16, 58 + y_off)], fill=white_color)
    # 紫色外袍/飘带
    draw.polygon([(20, 38 + y_off), (28, 38 + y_off), (20, 55 + y_off), (12, 50 + y_off)], fill=purple_color)
    draw.polygon([(36, 38 + y_off), (44, 38 + y_off), (52, 50 + y_off), (44, 55 + y_off)], fill=purple_color)

    # --- 5. 绘制头部 (Head) ---
    # 脸部
    draw.ellipse([23, 16 + y_off, 41, 34 + y_off], fill=skin_color)
    # 眼睛 (Q版大眼)
    eye_y = 26 + y_off
    draw.rectangle([27, eye_y, 29, eye_y + 2], fill=(40, 40, 40, 255))
    draw.rectangle([35, eye_y, 37, eye_y + 2], fill=(40, 40, 40, 255))
    # 腮红
    draw.point([(26, eye_y + 3), (38, eye_y + 3)], fill=(255, 150, 150, 180))

    # --- 6. 绘制前发与发饰 (Front Hair & Jade) ---
    # 刘海
    draw.chord([23, 16 + y_off, 41, 30 + y_off], start=180, end=360, fill=hair_color)
    # 玉饰
    jade_x = random.randint(25, 30)
    draw.ellipse([jade_x, 18 + y_off, jade_x + 3, 21 + y_off], fill=jade_color)
    draw.ellipse([64 - jade_x - 3, 18 + y_off, 64 - jade_x, 21 + y_off], fill=jade_color)

    # --- 7. 绘制小白兔 (White Rabbit) ---
    rabbit_x = 32
    rabbit_y = 42 + y_off
    # 兔子身体
    draw.ellipse([rabbit_x - 4, rabbit_y, rabbit_x + 4, rabbit_y + 6], fill=(255, 255, 255, 255))
    # 兔子耳朵
    draw.ellipse([rabbit_x - 3, rabbit_y - 3, rabbit_x - 1, rabbit_y + 1], fill=(255, 255, 255, 255))
    draw.ellipse([rabbit_x + 1, rabbit_y - 3, rabbit_x + 3, rabbit_y + 1], fill=(255, 255, 255, 255))
    # 兔子眼睛
    draw.point([(rabbit_x - 2, rabbit_y + 2), (rabbit_x + 2, rabbit_y + 2)], fill=(255, 100, 100, 255))

    # --- 8. 细节高光 (Highlights) ---
    # 头发高光
    draw.line([28, 18 + y_off, 36, 18 + y_off], fill=(80, 80, 90, 255), width=1)

    # --- 9. 纹理处理 (Texture Noise) ---
    add_texture_noise(img, intensity=12)

    # 保存图像
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()