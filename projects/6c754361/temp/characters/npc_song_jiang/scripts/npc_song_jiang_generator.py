import argparse
import random
from PIL import Image, ImageDraw, ImageColor

def add_noise(img, x0, y0, x1, y1, intensity=15):
    """
    为指定区域添加纹理噪点的辅助函数。
    通过对现有像素颜色进行随机偏移，模拟像素风的颗粒感。
    """
    pixels = img.load()
    x_start, x_end = sorted([max(0, x0), min(img.width - 1, x1)])
    y_start, y_end = sorted([max(0, y0), min(img.height - 1, y1)])
    
    for x in range(x_start, x_end + 1):
        for y in range(y_start, y_end + 1):
            r, g, b, a = pixels[x, y]
            if a > 0:  # 只处理非透明区域
                noise = random.randint(-intensity, intensity)
                new_r = max(0, min(255, r + noise))
                new_g = max(0, min(255, g + noise))
                new_b = max(0, min(255, b + noise))
                pixels[x, y] = (new_r, new_g, new_b, a)

def safe_ellipse(draw, coords, fill=None, outline=None, width=1):
    """安全绘制椭圆，确保坐标顺序正确"""
    x0, y0, x1, y1 = coords
    draw.ellipse([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill, outline=outline, width=width)

def safe_rectangle(draw, coords, fill=None, outline=None, width=1):
    """安全绘制矩形，确保坐标顺序正确"""
    x0, y0, x1, y1 = coords
    draw.rectangle([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=fill, outline=outline, width=width)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="输出图像路径")
    parser.add_argument('--seed', type=int, default=1, help="随机种子")
    args = parser.parse_args()
    
    # 设置随机种子
    random.seed(args.seed)
    
    # 图像尺寸与基础设置
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. 算法级颜色生成
    # 肤色：深色调变体
    skin_r = random.randint(60, 110)
    skin_g = int(skin_r * 0.7)
    skin_b = int(skin_r * 0.5)
    skin_color = (skin_r, skin_g, skin_b, 255)
    skin_shadow = (max(0, skin_r - 30), max(0, skin_g - 20), max(0, skin_b - 20), 255)
    
    # 官服颜色：紫色调变体
    robe_r = random.randint(80, 130)
    robe_b = random.randint(160, 220)
    robe_color = (robe_r, 30, robe_b, 255)
    robe_shadow = (max(0, robe_r - 40), 10, max(0, robe_b - 40), 255)
    robe_highlight = (min(255, robe_r + 40), 80, min(255, robe_b + 40), 255)
    
    # 天书颜色：泛黄纸张
    book_color = (240, 230, random.randint(140, 180), 255)
    
    # 云团颜色
    cloud_color = (180, 100, 255, random.randint(80, 150))

    # 2. 底层绘制：阴影与轮廓
    # 角色整体阴影（地面）
    safe_ellipse(draw, [16, 56, 48, 62], fill=(0, 0, 0, 60))
    
    # 3. 中层绘制：主体形状
    # 绘制身体 (矮胖身材)
    body_box = [18, 34, 46, 58]
    safe_rectangle(draw, body_box, fill=robe_color)
    # 绘制头部
    head_box = [22, 18, 42, 36]
    safe_ellipse(draw, head_box, fill=skin_color)
    
    # 绘制官服袖子
    safe_rectangle(draw, [14, 38, 22, 50], fill=robe_color) # 左袖
    safe_rectangle(draw, [42, 38, 50, 50], fill=robe_color) # 右袖
    
    # 4. 顶层绘制：细节与特效
    # 面部细节 (和善的面容)
    # 眼睛 (眯眯眼)
    draw.line([27, 26, 30, 26], fill=(20, 10, 0, 255), width=1)
    draw.line([34, 26, 37, 26], fill=(20, 10, 0, 255), width=1)
    # 嘴巴 (微笑)
    draw.point([(31, 31), (32, 32), (33, 31)], fill=(150, 50, 50, 255))
    
    # 官服破损效果 (随机小孔)
    for _ in range(random.randint(5, 10)):
        px = random.randint(20, 44)
        py = random.randint(36, 56)
        draw.point((px, py), fill=(0, 0, 0, 100))
    
    # 手持《天书》
    book_box = [38, 40, 54, 52]
    safe_rectangle(draw, book_box, fill=book_color, outline=(100, 80, 20, 255))
    # 书上的文字线条
    draw.line([41, 43, 51, 43], fill=(60, 50, 20, 200), width=1)
    draw.line([41, 46, 51, 46], fill=(60, 50, 20, 200), width=1)
    draw.line([41, 49, 51, 49], fill=(60, 50, 20, 200), width=1)
    
    # 头顶紫色云团特效 (多层半透明叠加)
    for i in range(3):
        cx = 32 + random.randint(-5, 5)
        cy = 10 + random.randint(-3, 3)
        cr = random.randint(8, 12)
        safe_ellipse(draw, [cx-cr, cy-cr//2, cx+cr, cy+cr//2], fill=cloud_color)

    # 5. 渲染优化：高光与阴影细节
    # 衣服阴影
    safe_rectangle(draw, [18, 54, 46, 58], fill=robe_shadow)
    # 头部阴影
    safe_ellipse(draw, [22, 32, 42, 36], fill=skin_shadow)
    # 衣服高光
    draw.line([20, 35, 44, 35], fill=robe_highlight, width=1)

    # 6. 纹理优化：添加像素噪点
    # 为皮肤添加纹理
    add_noise(img, 22, 18, 42, 36, intensity=10)
    # 为衣服添加纹理
    add_noise(img, 14, 34, 50, 58, intensity=15)
    # 为天书添加纹理
    add_noise(img, 38, 40, 54, 52, intensity=20)

    # 保存图像
    img.save(args.output, 'PNG')

if __name__ == '__main__':
    main()