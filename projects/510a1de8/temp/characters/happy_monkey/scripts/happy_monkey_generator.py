import argparse
import random
from PIL import Image, ImageDraw

def draw_base(draw, color, shapes):
    """核心绘图函数：根据形状类型和坐标列表绘制基础剪影或特征"""
    for shape_type, box in shapes:
        if shape_type == "o":
            draw.ellipse(box, fill=color)
        elif shape_type == "r":
            draw.rectangle(box, fill=color)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    random.seed(args.seed)
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 调色板: 0:金褐毛发, 1:肤色, 2:琥珀眼, 3:丝绸红, 4:木杖褐, 5:虎皮黄
    pal = [(184, 115, 51, 255), (255, 222, 173, 255), (255, 191, 0, 255), 
           (200, 20, 20, 255), (101, 67, 33, 255), (255, 165, 0, 255)]

    # 1. 绘制身体与四肢 (2头身比例)
    draw_base(draw, pal[0], [("o", (24, 38, 42, 58)), ("o", (20, 52, 28, 60)), ("o", (38, 52, 46, 60))])
    
    # 2. 绘制头部与耳朵 (Q版大头)
    draw_base(draw, pal[0], [("o", (12, 6, 52, 46)), ("o", (8, 18, 18, 30)), ("o", (46, 18, 56, 30))])
    # 脸部区域
    draw_base(draw, pal[1], [("o", (18, 16, 46, 42))])
    
    # 3. 核心特征：琥珀大眼与顽皮微笑
    for x_off in [0, 12]:
        draw_base(draw, pal[2], [("o", (23 + x_off, 24, 29 + x_off, 32))])
        draw.point((25 + x_off, 26), fill=(255, 255, 255, 255))
    draw.arc([27, 32, 37, 38], 0, 180, fill=(0, 0, 0, 255)) # 微笑

    # 4. 装备：红围巾与虎皮裙
    draw_base(draw, pal[3], [("r", (20, 40, 44, 44))]) # 围巾
    draw_base(draw, pal[5], [("r", (24, 46, 42, 54))]) # 虎皮裙
    for i in range(25, 45, 5): # 虎皮纹理循环
        draw.line([i, 46, i + 2, 54], fill=(0, 0, 0, 255), width=1)
    
    # 5. 武器：木杖
    draw.line([15, 25, 15, 60], fill=pal[4], width=3)
    draw_base(draw, pal[0], [("o", (12, 42, 18, 48))]) # 握住木杖的手

    # 6. 增加像素风格明暗噪点
    pix = img.load()
    for _ in range(800):
        x, y = random.randint(0, 63), random.randint(0, 63)
        r, g, b, a = pix[x, y]
        if a > 0:
            v = random.randint(-20, 20)
            pix[x, y] = (max(0, min(255, r + v)), max(0, min(255, g + v)), max(0, min(255, b + v)), a)

    img.save(args.output)

if __name__ == "__main__":
    main()