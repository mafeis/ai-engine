import argparse
import random
from PIL import Image, ImageDraw

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="生成一个Q版小恶魔侦察兵图像")
    parser.add_argument('--output', required=True, help="输出图像的路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子，影响生成结果")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 图像尺寸与基础设置
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 随机颜色方案
    skin_colors = [(180, 40, 40, 255), (100, 40, 150, 255), (40, 120, 180, 255)]
    helmet_colors = [(100, 100, 110, 255), (130, 110, 70, 255), (60, 60, 70, 255)]
    skin_color = random.choice(skin_colors)
    helmet_color = random.choice(helmet_colors)
    flag_color = (200, 20, 20, 255)
    gong_color = (240, 190, 40, 255)
    shadow_color = (0, 0, 0, 80)

    # 随机偏移量，体现“笨拙”感
    tilt = random.randint(-3, 3)
    bobbing = random.randint(-2, 2)

    # 1. 绘制投影 (最底层)
    draw.ellipse([18, 55, 46, 61], fill=shadow_color)

    # 2. 绘制背后的红旗
    # 旗杆
    pole_x = 42 + tilt
    draw.rectangle([pole_x, 15, pole_x + 2, 45], fill=(80, 50, 30, 255))
    # 旗面 (多边形，确保坐标顺序)
    flag_points = [
        (pole_x + 2, 15),
        (pole_x + 18, 20 + tilt),
        (pole_x + 18, 30 + tilt),
        (pole_x + 2, 35)
    ]
    draw.polygon(flag_points, fill=flag_color)

    # 3. 绘制身体 (Q版圆润)
    body_box = [24, 38 + bobbing, 42, 56 + bobbing]
    draw.ellipse(body_box, fill=skin_color)
    # 绘制短小的腿
    draw.rectangle([26, 54 + bobbing, 30, 59 + bobbing], fill=skin_color)
    draw.rectangle([36, 54 + bobbing, 40, 59 + bobbing], fill=skin_color)

    # 4. 绘制巨大的头盔 (遮住眼睛)
    # 头盔主体
    h_x0, h_y0, h_x1, h_y1 = 12, 18 + bobbing, 52, 46 + bobbing
    draw.ellipse([h_x0, h_y0, h_x1, h_y1], fill=helmet_color)
    # 头盔装饰 (如小角)
    draw.polygon([(15, 25 + bobbing), (10, 10 + bobbing), (25, 20 + bobbing)], fill=helmet_color)
    draw.polygon([(49, 25 + bobbing), (54, 10 + bobbing), (39, 20 + bobbing)], fill=helmet_color)
    # 头盔阴影线
    draw.arc([h_x0 + 2, h_y0 + 2, h_x1 - 2, h_y1 - 2], start=0, end=180, fill=(0, 0, 0, 50), width=2)

    # 5. 绘制手和小锣
    # 手
    hand_pos = [10, 44 + bobbing, 18, 52 + bobbing]
    draw.ellipse(hand_pos, fill=skin_color)
    # 锣 (圆形)
    gong_box = [4, 42 + bobbing, 22, 60 + bobbing]
    draw.ellipse(gong_box, fill=gong_color, outline=(180, 140, 30, 255), width=1)
    # 锣心
    draw.ellipse([10, 48 + bobbing, 16, 54 + bobbing], fill=(255, 230, 100, 255))

    # 6. 细节与高光
    # 头盔高光
    draw.ellipse([18, 22 + bobbing, 28, 28 + bobbing], fill=(255, 255, 255, 60))

    # 7. 纹理处理 (Texture Noise)
    # 遍历像素添加随机噪点，增加质感
    pixels = img.load()
    for y in range(size):
        for x in range(size):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # 根据种子生成噪点
                noise = random.randint(-15, 15)
                new_r = max(0, min(255, r + noise))
                new_g = max(0, min(255, g + noise))
                new_b = max(0, min(255, b + noise))
                pixels[x, y] = (new_r, new_g, new_b, a)

    # 8. 边缘描边 (像素风增强)
    # 简单的描边逻辑：如果透明像素邻近不透明像素，则填充深色
    final_img = img.copy()
    final_draw = ImageDraw.Draw(final_img)
    # 此处省略复杂描边，保持Q版清新感

    # 保存图像
    final_img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()