import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def add_noise(draw, coords, base_color, intensity=15):
    """
    为指定区域添加纹理噪点的辅助函数。
    coords: (x0, y0, x1, y1)
    """
    x0, y0, x1, y1 = coords
    x_start, x_end = min(x0, x1), max(x0, x1)
    y_start, y_end = min(y0, y1), max(y0, y1)
    
    for x in range(x_start, x_end + 1):
        for y in range(y_start, y_end + 1):
            if random.random() > 0.6:  # 40% 的概率添加噪点
                r, g, b = base_color[:3]
                offset = random.randint(-intensity, intensity)
                new_color = (
                    max(0, min(255, r + offset)),
                    max(0, min(255, g + offset)),
                    max(0, min(255, b + offset)),
                    255
                )
                draw.point((x, y), fill=new_color)

def safe_rect(draw, coords, fill=None, outline=None, width=1):
    """安全绘制矩形，确保坐标顺序正确"""
    x0, y0, x1, y1 = coords
    draw.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill, outline=outline, width=width)

def safe_ellipse(draw, coords, fill=None, outline=None, width=1):
    """安全绘制椭圆，确保坐标顺序正确"""
    x0, y0, x1, y1 = coords
    draw.ellipse([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill, outline=outline, width=width)

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
    
    # 1. 确定调色板 (基于种子生成)
    # 袍服主色调
    hue = random.randint(0, 360)
    robe_color = ImageColor.getrgb(f"hsl({hue}, {random.randint(30, 70)}%, {random.randint(40, 60)}%)")
    robe_shadow = tuple(max(0, c - 40) for c in robe_color)
    robe_light = tuple(min(255, c + 40) for c in robe_color)
    
    # 皮肤色
    skin_base = (255, random.randint(200, 230), random.randint(160, 190), 255)
    skin_shadow = (220, 180, 150, 255)
    
    # 纶巾颜色 (通常为深色或青色)
    hat_color = (random.randint(20, 50), random.randint(20, 50), random.randint(40, 80), 255)
    
    # 2. 绘制底层阴影/轮廓 (Layer 1)
    # 身体轮廓
    safe_rect(draw, (18, 35, 46, 60), fill=robe_shadow)
    # 头部轮廓
    safe_ellipse(draw, (22, 12, 42, 34), fill=(50, 50, 50, 255))
    
    # 3. 绘制主体层 (Layer 2)
    # 绘制袍服
    safe_rect(draw, (20, 34, 44, 58), fill=robe_color)
    # 绘制面部
    safe_ellipse(draw, (24, 14, 40, 32), fill=skin_base)
    
    # 绘制纶巾 (头巾)
    safe_rect(draw, (22, 10, 42, 18), fill=hat_color)
    safe_rect(draw, (28, 6, 36, 12), fill=hat_color) # 巾顶
    
    # 绘制三绺长须
    beard_color = (40, 40, 40, 255)
    draw.line([(28, 30), (27, 42)], fill=beard_color, width=1) # 左
    draw.line([(32, 32), (32, 45)], fill=beard_color, width=1) # 中
    draw.line([(36, 30), (37, 42)], fill=beard_color, width=1) # 右
    
    # 绘制精明的眼神
    eye_color = (20, 20, 20, 255)
    draw.point([(29, 22), (30, 22), (34, 22), (35, 22)], fill=eye_color) # 细长的眼睛
    
    # 绘制羽扇
    fan_base = (240, 240, 240, 255)
    fan_handle = (100, 70, 40, 255)
    # 扇柄
    draw.line([(44, 45), (50, 35)], fill=fan_handle, width=1)
    # 扇面 (像素化羽毛感)
    safe_ellipse(draw, (45, 25, 58, 40), fill=fan_base)
    
    # 4. 绘制高光与细节 (Layer 3)
    # 袍服高光
    draw.line([(21, 35), (21, 55)], fill=robe_light, width=1)
    # 纶巾装饰
    safe_rect(draw, (31, 12, 33, 14), fill=(200, 200, 100, 255)) # 巾前饰品
    
    # 羽扇上的闪烁白色光点
    for _ in range(5):
        px = random.randint(46, 56)
        py = random.randint(26, 38)
        draw.point((px, py), fill=(255, 255, 255, 255))
        
    # 5. 添加表面纹理 (Texture Noise)
    # 为袍服添加纹理
    add_noise(draw, (20, 34, 44, 58), robe_color, intensity=10)
    # 为纶巾添加纹理
    add_noise(draw, (22, 10, 42, 18), hat_color, intensity=8)
    # 为面部添加极轻微纹理
    add_noise(draw, (24, 14, 40, 32), skin_base, intensity=5)

    # 最终缩放以增强像素感 (可选，但此处保持64x64)
    # img = img.resize((512, 512), resample=Image.NEAREST)
    
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()