import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 基础参数
    width, height = 64, 64
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 随机化视觉方案
    skin_color = (255, random.randint(210, 235), random.randint(180, 200), 255)
    robe_green = random.randint(100, 180)
    robe_color = (random.randint(20, 60), robe_green, random.randint(20, 60), 255)
    robe_dark = (robe_color[0]//2, robe_color[1]//2, robe_color[2]//2, 255)
    staff_side = random.choice([-1, 1]) # 1 为右侧，-1 为左侧
    beard_fullness = random.randint(12, 18)
    peach_hue = random.randint(150, 200)
    peach_color = (255, peach_hue, peach_hue, 255)

    def get_safe_box(x0, y0, x1, y1):
        """确保坐标满足 x0 < x1 且 y0 < y1"""
        return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]

    def add_texture_noise(draw_obj, box, intensity=15):
        """在指定区域添加像素级噪点纹理"""
        x0, y0, x1, y1 = [int(c) for c in box]
        for px in range(x0, x1 + 1):
            for py in range(y0, y1 + 1):
                if 0 <= px < width and 0 <= py < height:
                    current_pixel = img.getpixel((px, py))
                    if current_pixel[3] > 0: # 仅处理非透明像素
                        noise = random.randint(-intensity, intensity)
                        new_color = tuple(max(0, min(255, c + noise)) for c in current_pixel[:3]) + (current_pixel[3],)
                        draw_obj.point((px, py), fill=new_color)

    # 1. 绘制投影 (Shadow)
    shadow_box = get_safe_box(16, 58, 48, 63)
    draw.ellipse(shadow_box, fill=(0, 0, 0, 60))

    # 2. 绘制木杖 (Wooden Staff) - 放在身体后面或侧面
    staff_x = 32 + (staff_side * 20)
    staff_box = get_safe_box(staff_x - 2, 15, staff_x + 2, 60)
    draw.rectangle(staff_box, fill=(101, 67, 33, 255))
    add_texture_noise(draw, staff_box)

    # 3. 绘制叶子长袍 (Leaf Robe) - Q版短小身体
    robe_box = get_safe_box(20, 35, 44, 58)
    draw.ellipse(robe_box, fill=robe_color)
    # 绘制叶片边缘细节
    for i in range(5):
        lx = random.randint(20, 40)
        ly = random.randint(45, 58)
        draw.chord(get_safe_box(lx, ly, lx+6, ly+6), 0, 360, fill=robe_dark)
    add_texture_noise(draw, robe_box)

    # 4. 绘制头部 (Head)
    head_box = get_safe_box(20, 10, 44, 34)
    draw.ellipse(head_box, fill=skin_color)
    add_texture_noise(draw, head_box, intensity=10)

    # 5. 绘制长胡须 (Long White Beard) - 垂到地面
    beard_points = [
        (32 - beard_fullness, 28), (32 + beard_fullness, 28),
        (32 + beard_fullness - 4, 62), (32 - beard_fullness + 4, 62)
    ]
    draw.polygon(beard_points, fill=(240, 240, 240, 255))
    # 胡须纹理线
    for _ in range(10):
        bx = random.randint(32 - beard_fullness + 5, 32 + beard_fullness - 5)
        draw.line([(bx, 30), (bx + random.randint(-2, 2), 60)], fill=(200, 200, 200, 255), width=1)

    # 6. 绘制面部细节 (Eyes) - 眯眯眼
    eye_y = 22
    draw.line([(26, eye_y), (30, eye_y)], fill=(60, 40, 20, 255), width=1)
    draw.line([(34, eye_y), (38, eye_y)], fill=(60, 40, 20, 255), width=1)

    # 7. 绘制仙桃 (Glowing Peach)
    peach_x = staff_x
    peach_y = 15
    peach_box = get_safe_box(peach_x - 5, peach_y - 6, peach_x + 5, peach_y + 4)
    draw.ellipse(peach_box, fill=peach_color)
    # 桃子尖尖
    draw.polygon([(peach_x - 2, peach_y - 5), (peach_x + 2, peach_y - 5), (peach_x, peach_y - 9)], fill=peach_color)
    
    # 8. 绘制光晕与高光 (Glow & Highlights)
    # 桃子光晕
    glow_box = get_safe_box(peach_x - 8, peach_y - 9, peach_x + 8, peach_y + 7)
    draw.ellipse(glow_box, outline=(255, 255, 200, 100), width=1)
    # 头部高光
    draw.point((28, 15), fill=(255, 255, 255, 180))
    draw.point((29, 15), fill=(255, 255, 255, 180))

    # 最终全图微调噪点 (增加像素风质感)
    add_texture_noise(draw, [0, 0, 63, 63], intensity=5)

    # 保存图像
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()