import argparse
import math
from PIL import Image, ImageDraw

def draw_character(draw, ox, oy, action, frame):
    """
    ox, oy: 帧的左上角坐标
    action: 0: Idle, 1: Walk, 2: Attack
    frame: 0-3
    """
    # 基础颜色
    C_SKIN = (255, 224, 189, 255)
    C_HAIR = (20, 20, 25, 255)
    C_PURPLE = (147, 112, 219, 255)
    C_WHITE = (255, 255, 255, 255)
    C_JADE = (0, 168, 107, 255)
    C_RABBIT = (255, 250, 250, 255)
    C_AURA = (200, 230, 255, 60)
    C_MAGIC = (255, 255, 200, 180)

    # 动画偏移量计算
    bob = 0
    leg_swing = 0
    arm_pos = 0
    magic_scale = 0
    
    if action == 0: # Idle: 呼吸起伏
        bob = int(math.sin(frame * math.pi / 2) * 3)
    elif action == 1: # Walk: 左右晃动与腿部模拟
        bob = int(abs(math.sin(frame * math.pi / 2)) * 2)
        leg_swing = [2, -2, 2, -2][frame]
    elif action == 2: # Attack: 蓄力到释放
        arm_pos = [0, -4, 8, 2][frame]
        magic_scale = [0, 4, 12, 6][frame]

    cx, cy = ox + 32, oy + 32 + bob

    # 1. 绘制光晕 (Aura)
    aura_r = 22 + int(math.sin(frame) * 2)
    draw.ellipse([cx - aura_r, cy - aura_r, cx + aura_r, cy + aura_r], fill=C_AURA)

    # 2. 后发 (Back Hair)
    draw.rectangle([cx - 12, cy - 10, cx + 12, cy + 18], fill=C_HAIR)
    draw.chord([cx - 12, cy + 10, cx + 12, cy + 26], 0, 180, fill=C_HAIR)

    # 3. 裙摆 (Hanfu Dress)
    # 走路时裙摆会有偏移
    dress_off = leg_swing if action == 1 else 0
    pts = [(cx - 14 + dress_off, cy + 24), (cx + 14 + dress_off, cy + 24), 
           (cx + 8, cy + 4), (cx - 8, cy + 4)]
    draw.polygon(pts, fill=C_WHITE)
    draw.rectangle([cx - 10 + dress_off, cy + 18, cx + 10 + dress_off, cy + 24], fill=C_PURPLE)

    # 4. 头部 (Head)
    draw.ellipse([cx - 10, cy - 18, cx + 10, cy + 2], fill=C_SKIN)
    # 眼睛
    draw.point([(cx - 4, cy - 8), (cx + 4, cy - 8)], fill=(40, 40, 40, 255))
    
    # 5. 前发与发饰 (Front Hair & Jade)
    draw.rectangle([cx - 10, cy - 18, cx + 10, cy - 12], fill=C_HAIR)
    draw.rectangle([cx - 2, cy - 22, cx + 2, cy - 16], fill=C_JADE) # 簪子

    # 6. 手臂与兔子 (Arms & Rabbit)
    if action == 2: # 攻击动作
        # 施法手臂
        draw.line([cx + 6, cy + 4, cx + 12 + arm_pos, cy + 4 - arm_pos//2], fill=C_SKIN, width=3)
        if magic_scale > 0:
            m_r = magic_scale
            draw.ellipse([cx + 15 + arm_pos - m_r, cy - m_r, cx + 15 + arm_pos + m_r, cy + m_r], fill=C_MAGIC)
    else:
        # 抱兔子
        draw.ellipse([cx - 6, cy + 2, cx + 6, cy + 12], fill=C_RABBIT) # 兔子身体
        draw.ellipse([cx - 4, cy + 0, cx - 1, cy + 4], fill=C_RABBIT) # 兔子耳朵
        draw.ellipse([cx + 1, cy + 0, cx + 4, cy + 4], fill=C_RABBIT) # 兔子耳朵
        # 手臂环抱
        draw.arc([cx - 10, cy + 2, cx + 10, cy + 14], 0, 180, fill=C_PURPLE, width=3)

    # 7. 飘带 (Flowing Ribbons)
    ribbon_off = int(math.sin(frame * 0.8) * 4)
    draw.line([cx - 12, cy + 4, cx - 20 - ribbon_off, cy + 20], fill=C_PURPLE, width=2)
    draw.line([cx + 12, cy + 4, cx + 20 + ribbon_off, cy + 20], fill=C_PURPLE, width=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    fw, fh = 64, 64
    cols, rows = 4, 3
    sheet_w, sheet_h = fw * cols, fh * rows

    # 创建透明画布
    canvas = Image.new('RGBA', (sheet_w, sheet_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # 动作定义: 0=Idle, 1=Walk, 2=Attack
    for row in range(rows):
        for col in range(cols):
            draw_character(draw, col * fw, row * fh, row, col)

    # 模拟像素风：缩小再放大（可选，此处直接输出清晰矢量风格的像素图）
    # 如果需要更硬核的像素感，可以取消下面注释
    # canvas = canvas.resize((sheet_w//2, sheet_h//2), Image.NEAREST)
    # canvas = canvas.resize((sheet_w, sheet_h), Image.NEAREST)

    canvas.save(args.output)

if __name__ == "__main__":
    main()