import argparse
from PIL import Image, ImageDraw

def draw_frame(canvas, x_offset, y_offset, action, frame_idx):
    # 颜色定义
    PIG_PINK = (255, 182, 193, 255)
    PIG_DARK_PINK = (255, 140, 157, 255)
    ROBE_BLACK = (30, 30, 30, 255)
    MELON_GREEN = (34, 139, 34, 255)
    MELON_DARK = (0, 100, 0, 255)
    RAKE_BROWN = (139, 69, 19, 255)
    RAKE_GRAY = (169, 169, 169, 255)
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)

    draw = ImageDraw.Draw(canvas)
    
    # 基础坐标 (居中)
    cx, cy = x_offset + 32, y_offset + 32
    
    # 动画参数计算
    bounce = 0
    melon_roll = 0
    rake_angle = 0
    rake_ext = 0
    eye_closed = False
    
    if action == "idle":
        # 呼吸效果
        bounce = [0, 1, 2, 1][frame_idx]
        eye_closed = frame_idx > 1
    elif action == "walk":
        # 滚动与颠簸
        bounce = [0, -2, 0, -2][frame_idx]
        melon_roll = frame_idx * 4
        rake_angle = [-5, 5, -5, 5][frame_idx]
    elif action == "attack":
        # 蓄力挥动
        bounce = [0, -4, 2, 0][frame_idx]
        rake_ext = [0, -8, 12, 4][frame_idx]
        rake_angle = [0, -30, 45, 10][frame_idx]

    # 1. 绘制大西瓜 (底座)
    melon_rect = [cx-22, cy+8, cx+22, cy+28]
    draw.ellipse(melon_rect, fill=MELON_GREEN, outline=MELON_DARK, width=2)
    # 西瓜纹路
    for i in range(-2, 3):
        sx = cx + i*8 + (melon_roll % 8) - 4
        if cx-18 < sx < cx+18:
            draw.line([sx, cy+10, sx-2, cy+26], fill=MELON_DARK, width=2)

    # 2. 绘制猪八戒身体 (躺在西瓜上)
    body_y = cy + bounce
    # 黑色僧袍
    draw.ellipse([cx-18, body_y-10, cx+15, body_y+12], fill=ROBE_BLACK)
    # 露出的肚皮
    draw.ellipse([cx-10, body_y, cx+8, body_y+10], fill=PIG_PINK)
    
    # 3. 头部
    head_x = cx + 10
    head_y = body_y - 8
    draw.ellipse([head_x-10, head_y-10, head_x+10, head_y+10], fill=PIG_PINK)
    # 猪鼻子
    draw.rectangle([head_x+4, head_y-2, head_x+11, head_y+4], fill=PIG_DARK_PINK)
    draw.point([(head_x+6, head_y), (head_x+9, head_y)], fill=BLACK)
    # 眼睛
    if eye_closed:
        draw.line([head_x+2, head_y-4, head_x+5, head_y-4], fill=BLACK)
    else:
        draw.point([(head_x+3, head_y-4)], fill=BLACK)
    # 耳朵
    draw.polygon([head_x-2, head_y-8, head_x-8, head_y-14, head_x-6, head_y-4], fill=PIG_DARK_PINK)

    # 4. 九齿钉耙 (作为痒痒挠)
    rake_base_x = cx - 12 + rake_ext
    rake_base_y = body_y - 5
    # 耙柄
    handle_end_x = rake_base_x - 15
    handle_end_y = rake_base_y - 10 + rake_angle
    draw.line([rake_base_x, rake_base_y, handle_end_x, handle_end_y], fill=RAKE_BROWN, width=2)
    # 耙头 (九齿简化)
    head_top = [handle_end_x-4, handle_end_y-4, handle_end_x+4, handle_end_y+4]
    draw.rectangle(head_top, fill=RAKE_GRAY)
    for i in range(-3, 4, 2):
        draw.line([handle_end_x+i, handle_end_y, handle_end_x+i, handle_end_y-6], fill=RAKE_GRAY, width=1)

    # 5. 手臂 (抱着耙子)
    draw.line([cx, body_y, rake_base_x, rake_base_y], fill=ROBE_BLACK, width=4)
    draw.ellipse([rake_base_x-3, rake_base_y-3, rake_base_x+3, rake_base_y+3], fill=PIG_PINK)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    frame_w, frame_h = 64, 64
    cols, rows = 4, 3
    actions = ["idle", "walk", "attack"]

    # 创建画布
    sheet = Image.new('RGBA', (frame_w * cols, frame_h * rows), (0, 0, 0, 0))

    for row_idx, action in enumerate(actions):
        for col_idx in range(cols):
            x = col_idx * frame_w
            y = row_idx * frame_h
            draw_frame(sheet, x, y, action, col_idx)

    # 保存结果
    sheet.save(args.output)

if __name__ == "__main__":
    main()