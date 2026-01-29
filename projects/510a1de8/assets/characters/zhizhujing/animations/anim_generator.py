import argparse
from PIL import Image, ImageDraw

def draw_sprite(draw, ox, oy, action, frame_idx):
    """
    绘制 zhizhujing 角色
    action: 0=Idle, 1=Walk, 2=Attack
    frame_idx: 0-3
    """
    # 基础颜色
    C_SKIN = (255, 224, 189, 255)
    C_PURPLE_DARK = (48, 25, 52, 255)
    C_PURPLE_LIGHT = (147, 112, 219, 255)
    C_EYE = (128, 0, 128, 255)
    C_BLACK = (20, 20, 20, 255)
    C_WHITE = (255, 255, 255, 255)

    # 动画偏移量
    bob = 0
    leg_swing = 0
    arm_swing = 0
    attack_ext = 0
    body_tilt = 0

    if action == 0:  # Idle
        bob = [0, 1, 2, 1][frame_idx]
    elif action == 1:  # Walk
        bob = [0, 2, 0, 2][frame_idx]
        leg_swing = [4, -4, 4, -4][frame_idx]
        arm_swing = [-3, 3, -3, 3][frame_idx]
    elif action == 2:  # Attack
        if frame_idx == 0: # 蓄力
            body_tilt = -2
            attack_ext = -2
        elif frame_idx == 1: # 突刺
            body_tilt = 5
            attack_ext = 10
        elif frame_idx == 2: # 收招
            body_tilt = 2
            attack_ext = 5
        else: # 回位
            body_tilt = 0
            attack_ext = 0

    # 1. 绘制背后的 4 条蜘蛛腿 (Fuzzy Spider Legs)
    leg_color = C_BLACK
    leg_width = 3
    s_legs = [
        [(ox+15, oy+35), (ox+5, oy+20-bob), (ox-5, oy+30+attack_ext)], # 左上
        [(ox+15, oy+40), (ox+2, oy+45-bob), (ox-8, oy+55+attack_ext)], # 左下
        [(ox+49, oy+35), (ox+59, oy+20-bob), (ox+69, oy+30+attack_ext)], # 右上
        [(ox+49, oy+40), (ox+62, oy+45-bob), (ox+72, oy+55+attack_ext)]  # 右下
    ]
    for leg in s_legs:
        draw.line(leg, fill=leg_color, width=leg_width)

    # 2. 绘制头发 (后部)
    draw.ellipse([ox+18, oy+10+bob, ox+46, oy+40+bob], fill=C_PURPLE_DARK)

    # 3. 绘制腿 (人类)
    draw.rectangle([ox+26+leg_swing, oy+50+bob, ox+30+leg_swing, oy+62], fill=C_SKIN)
    draw.rectangle([ox+34-leg_swing, oy+50+bob, ox+38-leg_swing, oy+62], fill=C_SKIN)

    # 4. 绘制哥特裙子 (Purple Gothic Lolita Dress)
    # 裙摆
    draw.polygon([
        (ox+20-body_tilt, oy+55+bob), (ox+44-body_tilt, oy+55+bob),
        (ox+50-body_tilt, oy+40+bob), (ox+14-body_tilt, oy+40+bob)
    ], fill=C_PURPLE_LIGHT)
    # 裙子细节 (黑边)
    draw.line([(ox+14-body_tilt, oy+40+bob), (ox+50-body_tilt, oy+40+bob)], fill=C_BLACK, width=2)
    # 上身
    draw.rectangle([ox+25-body_tilt, oy+35+bob, ox+39-body_tilt, oy+45+bob], fill=C_PURPLE_DARK)

    # 5. 绘制手臂
    draw.line([(ox+25-body_tilt, oy+38+bob), (ox+20-body_tilt+arm_swing, oy+50+bob)], fill=C_SKIN, width=3)
    draw.line([(ox+39-body_tilt, oy+38+bob), (ox+44-body_tilt-arm_swing, oy+50+bob)], fill=C_SKIN, width=3)

    # 6. 绘制头部
    head_rect = [ox+22-body_tilt, oy+15+bob, ox+42-body_tilt, oy+35+bob]
    draw.ellipse(head_rect, fill=C_SKIN)
    
    # 头发 (前部/刘海)
    draw.chord([ox+22-body_tilt, oy+15+bob, ox+42-body_tilt, oy+28+bob], start=180, end=360, fill=C_PURPLE_DARK)
    
    # 眼睛 (Large Purple Eyes)
    draw.ellipse([ox+25-body_tilt, oy+24+bob, ox+30-body_tilt, oy+30+bob], fill=C_EYE)
    draw.ellipse([ox+34-body_tilt, oy+24+bob, ox+39-body_tilt, oy+30+bob], fill=C_EYE)
    draw.point([(ox+27-body_tilt, oy+26+bob), (ox+36-body_tilt, oy+26+bob)], fill=C_WHITE)

    # 嘴巴 (Mischievous Grin)
    draw.arc([ox+28-body_tilt, oy+28+bob, ox+36-body_tilt, oy+33+bob], start=0, end=180, fill=C_BLACK, width=1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    frame_w, frame_h = 64, 64
    cols, rows = 4, 3
    
    # 创建透明画布
    sheet = Image.new('RGBA', (frame_w * cols, frame_h * rows), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    # 动作定义: 0=Idle, 1=Walk, 2=Attack
    for row in range(rows):
        for col in range(cols):
            ox = col * frame_w
            oy = row * frame_h
            draw_sprite(draw, ox, oy, row, col)

    # 保存结果
    sheet.save(args.output)

if __name__ == "__main__":
    main()