import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def main():
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="生成Q版鱼人角色图像")
    parser.add_argument('--output', required=True, help="输出文件路径 (PNG)")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()

    # 设置随机种子
    random.seed(args.seed)

    # 基础参数设置
    width, height = 64, 64
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 颜色方案生成 (基于种子)
    # 鱼人皮肤颜色 (蓝色系)
    base_blue_h = random.randint(180, 220)
    skin_color = ImageColor.getrgb(f"hsl({base_blue_h}, {random.randint(50, 90)}%, {random.randint(40, 60)}%)")
    skin_dark = ImageColor.getrgb(f"hsl({base_blue_h}, {random.randint(50, 90)}%, {random.randint(20, 35)}%)")
    skin_light = ImageColor.getrgb(f"hsl({base_blue_h}, {random.randint(50, 90)}%, {random.randint(70, 85)}%)")

    # 海藻盔甲颜色 (绿色系)
    armor_color = ImageColor.getrgb(f"hsl({random.randint(80, 140)}, {random.randint(40, 70)}%, {random.randint(30, 50)}%)")
    
    # 泡泡法杖/三叉戟颜色
    trident_color = random.choice([(255, 215, 0, 255), (135, 206, 250, 255), (192, 192, 192, 255)])

    # 1. 绘制投影 (Shadow)
    shadow_color = (0, 0, 0, 60)
    draw.ellipse([16, 54, 48, 62], fill=shadow_color)

    # 2. 基础轮廓绘制 (分层)
    
    # 身体 (Body)
    body_rect = [22, 35, 42, 55]
    draw.ellipse(body_rect, fill=skin_color)
    
    # 头部 (Head) - Q版大头
    head_rect = [14, 10, 50, 42]
    draw.ellipse(head_rect, fill=skin_color)

    # 鱼鳍 (Fins) - 左右两侧
    draw.polygon([(14, 20), (6, 25), (14, 30)], fill=skin_dark)
    draw.polygon([(50, 20), (58, 25), (50, 30)], fill=skin_dark)

    # 3. 细节绘制
    
    # 突出的眼睛 (Bulging Eyes)
    eye_y = 22
    eye_size = random.randint(10, 14)
    # 左眼
    draw.ellipse([10, eye_y, 10 + eye_size, eye_y + eye_size], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    draw.ellipse([14, eye_y + 4, 18, eye_y + 8], fill=(0, 0, 0, 255)) # 瞳孔
    # 右眼
    draw.ellipse([54 - eye_size, eye_y, 54, eye_y + eye_size], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    draw.ellipse([46, eye_y + 4, 50, eye_y + 8], fill=(0, 0, 0, 255)) # 瞳孔

    # 海藻盔甲 (Seaweed Armor)
    # 简单的胸甲
    draw.rectangle([24, 40, 40, 48], fill=armor_color)
    # 肩部海藻
    draw.chord([20, 35, 30, 45], start=0, end=180, fill=armor_color)
    draw.chord([34, 35, 44, 45], start=0, end=180, fill=armor_color)

    # 泡泡法杖/三叉戟 (Bubble Wand / Trident)
    # 手臂
    draw.line([42, 45, 50, 40], fill=skin_color, width=3)
    # 法杖长柄
    draw.line([52, 15, 52, 55], fill=trident_color, width=2)
    # 三叉戟头部
    draw.line([48, 15, 56, 15], fill=trident_color, width=2)
    draw.line([48, 10, 48, 15], fill=trident_color, width=2)
    draw.line([52, 8, 52, 15], fill=trident_color, width=2)
    draw.line([56, 10, 56, 15], fill=trident_color, width=2)
    
    # 泡泡细节 (Bubble)
    if random.random() > 0.5:
        draw.ellipse([48, 2, 56, 10], outline=(200, 240, 255, 200), width=1)

    # 4. 高光与纹理处理 (Texture Noise)
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # 随机像素噪点增加质感
                noise = random.randint(-15, 15)
                # 简单的顶部高光逻辑
                highlight = 20 if y < 30 else 0
                
                new_r = max(0, min(255, r + noise + highlight))
                new_g = max(0, min(255, g + noise + highlight))
                new_b = max(0, min(255, b + noise + highlight))
                
                # 鱼鳞纹理模拟 (周期性噪点)
                if (x + y) % 4 == 0 and y > 30:
                    new_r = max(0, min(255, new_r + 10))
                    new_g = max(0, min(255, new_g + 10))
                
                pixels[x, y] = (new_r, new_g, new_b, a)

    # 5. 保存图像
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()