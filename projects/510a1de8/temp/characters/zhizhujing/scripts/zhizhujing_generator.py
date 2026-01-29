import argparse
import random
from PIL import Image, ImageDraw

def main():
    # 1. 脚本接口处理
    parser = argparse.ArgumentParser(description="生成一个Q版蜘蛛娘角色图像")
    parser.add_argument('--output', required=True, help="输出图像的路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子，影响生成结果")
    args = parser.parse_args()

    # 2. 设置随机种子
    random.seed(args.seed)

    # 3. 初始化画布 (64x64, RGBA 透明背景)
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 4. 算法级逻辑：定义基于种子的颜色方案
    # 皮肤色 (浅色系)
    skin_color = (255, random.randint(210, 230), random.randint(190, 210), 255)
    # 头发颜色 (深紫色、黑色或银色)
    hair_color = random.choice([
        (48, 25, 52, 255),   # 深紫
        (20, 20, 20, 255),   # 黑色
        (200, 180, 220, 255) # 浅紫银
    ])
    # 裙子主色 (哥特萝莉紫)
    dress_main = (random.randint(80, 120), 0, random.randint(130, 180), 255)
    dress_accent = (20, 20, 20, 255) # 黑色蕾丝边
    # 眼睛颜色 (大紫色)
    eye_color = (random.randint(180, 220), 50, 255, 255)
    # 蜘蛛腿颜色
    leg_color = (30, 10, 40, 255)

    # 5. 分层绘制逻辑

    # --- 第一层：背后的蜘蛛腿 (4条) ---
    # 确保坐标 x0 < x1, y0 < y1
    leg_coords = [
        (10, 20, 25, 45), (5, 30, 20, 50),  # 左侧两条
        (39, 20, 54, 45), (44, 30, 59, 50)   # 右侧两条
    ]
    for i, (x0, y0, x1, y1) in enumerate(leg_coords):
        # 绘制腿的基础线条
        if i < 2: # 左侧
            draw.arc([x0, y0, x1, y1], start=180, end=270, fill=leg_color, width=3)
        else: # 右侧
            draw.arc([x0, y0, x1, y1], start=270, end=0, fill=leg_color, width=3)
        
        # 添加“毛茸茸”的质感 (随机像素点)
        for _ in range(40):
            fx = random.randint(x0, x1)
            fy = random.randint(y0, y1)
            if 0 <= fx < 64 and 0 <= fy < 64:
                draw.point((fx, fy), fill=leg_color)

    # --- 第二层：身体与哥特裙 ---
    # 裙子主体 (梯形/钟形)
    draw.polygon([(20, 58), (44, 58), (38, 38), (26, 38)], fill=dress_main)
    # 裙摆黑色边框 (蕾丝感)
    draw.line([(20, 58), (44, 58)], fill=dress_accent, width=2)
    # 小手
    draw.ellipse([18, 42, 24, 48], fill=skin_color)
    draw.ellipse([40, 42, 46, 48], fill=skin_color)

    # --- 第三层：头部基础 ---
    # 脸部
    draw.ellipse([16, 8, 48, 40], fill=skin_color)
    
    # 头发 (覆盖头部上方)
    # 绘制发型轮廓
    draw.chord([15, 5, 49, 30], start=180, end=0, fill=hair_color)
    # 鬓角
    draw.rectangle([15, 20, 20, 38], fill=hair_color)
    draw.rectangle([44, 20, 49, 38], fill=hair_color)
    # 刘海 (锯齿状)
    for i in range(16, 48, 4):
        draw.polygon([(i, 20), (i+4, 20), (i+2, 26)], fill=hair_color)

    # --- 第四层：面部细节 (大眼睛与坏笑) ---
    # 左眼
    draw.ellipse([22, 22, 30, 34], fill=(255, 255, 255, 255)) # 眼白
    draw.ellipse([24, 24, 29, 32], fill=eye_color)           # 瞳孔
    # 右眼
    draw.ellipse([34, 22, 42, 34], fill=(255, 255, 255, 255)) # 眼白
    draw.ellipse([35, 24, 40, 32], fill=eye_color)           # 瞳孔
    
    # 坏笑 (Mischievous grin)
    # 使用小折线表示
    draw.line([(28, 35), (32, 37), (36, 35)], fill=(0, 0, 0, 255), width=1)

    # --- 第五层：高光与装饰 ---
    # 眼睛高光
    draw.point((25, 25), fill=(255, 255, 255, 255))
    draw.point((36, 25), fill=(255, 255, 255, 255))
    # 裙子上的小蝴蝶结 (黑色)
    draw.rectangle([30, 40, 34, 42], fill=dress_accent)

    # 6. 纹理处理 (Texture Noise)
    # 遍历所有像素，对非透明区域添加随机噪点增加质感
    pixels = img.load()
    for y in range(size):
        for x in range(size):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # 产生轻微的颜色偏差
                noise = random.randint(-12, 12)
                new_r = max(0, min(255, r + noise))
                new_g = max(0, min(255, g + noise))
                new_b = max(0, min(255, b + noise))
                pixels[x, y] = (new_r, new_g, new_b, a)

    # 7. 保存结果
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()