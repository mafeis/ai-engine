import argparse
from PIL import Image, ImageDraw

def draw_pixel_rect(draw, x, y, w, h, color, outline=None):
    """绘制带边框的像素矩形"""
    draw.rectangle([x, y, x + w, y + h], fill=color, outline=outline)

def draw_general(draw, ox, oy, action, frame_idx):
    # 基础颜色定义
    BRONZE = (139, 69, 19)
    BRONZE_LIGHT = (205, 127, 50)
    BRONZE_DARK = (80, 40, 10)
    RED_EYE = (255, 0, 0)
    IRON = (70, 70, 70)
    IRON_DARK = (30, 30, 30)

    # 动画参数计算
    bob = 0
    leg_l_off, leg_r_off = 0, 0
    arm_l_off, arm_r_off = 0, 0
    weapon_pos = (0, 0)
    chain_points = []

    if action == "idle":
        # 呼吸效果：上下微动
        bob = [0, 1, 2, 1][frame_idx % 4]
        eye_glow = [255, 150, 255, 200][frame_idx % 4]
        RED_EYE = (eye_glow, 0, 0)
        weapon_pos = (45, 35 + bob)
        
    elif action == "walk":
        # 行走效果：腿部交替，身体起伏
        bob = [0, 2, 0, 2][frame_idx % 4]
        leg_l_off = [0, -6, 0, 6][frame_idx % 4]
        leg_r_off = [0, 6, 0, -6][frame_idx % 4]
        arm_l_off = leg_r_off
        weapon_pos = (45 + leg_l_off//2, 35 + bob)

    elif action == "attack":
        # 攻击序列：蓄力 -> 挥动 -> 击打 -> 收招
        if frame_idx == 0: # 蓄力
            bob = 2
            weapon_pos = (10, 25)
            arm_r_off = -10
        elif frame_idx == 1: # 挥动
            bob = 0
            weapon_pos = (32, 5)
            arm_r_off = -20
        elif frame_idx == 2: # 击打（延伸）
            bob = 4
            weapon_pos = (55, 45)
            arm_r_off = 10
        else: # 收招
            bob = 1
            weapon_pos = (45, 35)
            arm_r_off = 0

    # 1. 绘制腿部 (Legs)
    draw_pixel_rect(draw, ox+20, oy+45+bob+leg_l_off, 8, 12, BRONZE_DARK) # 左腿
    draw_pixel_rect(draw, ox+36, oy+45+bob+leg_r_off, 8, 12, BRONZE_DARK) # 右腿

    # 2. 绘制躯干 (Torso - 巨大体型)
    draw_pixel_rect(draw, ox+16, oy+20+bob, 32, 28, BRONZE, BRONZE_DARK)
    # 胸甲纹路
    draw.line([ox+20, oy+30+bob, ox+44, oy+30+bob], fill=BRONZE_LIGHT)
    draw.line([ox+20, oy+35+bob, ox+44, oy+35+bob], fill=BRONZE_LIGHT)

    # 3. 绘制手臂 (Arms)
    draw_pixel_rect(draw, ox+8, oy+25+bob+arm_l_off, 10, 18, BRONZE, BRONZE_DARK) # 左臂
    draw_pixel_rect(draw, ox+46, oy+25+bob+arm_r_off, 10, 18, BRONZE, BRONZE_DARK) # 右臂

    # 4. 绘制头部 (Head)
    draw_pixel_rect(draw, ox+24, oy+8+bob, 16, 16, BRONZE, BRONZE_DARK)
    # 头盔缝隙与红光
    draw_pixel_rect(draw, ox+24, oy+14+bob, 16, 3, (20, 10, 0))
    draw.point([(ox+28, oy+15+bob), (ox+35, oy+15+bob)], fill=RED_EYE)

    # 5. 绘制流星锤 (Morning Star)
    # 链条
    handle_pos = (ox+51, oy+35+bob+arm_r_off)
    target_wp = (ox + weapon_pos[0], oy + weapon_pos[1])
    draw.line([handle_pos, target_wp], fill=IRON, width=1)
    # 锤头 (带刺球体)
    mx, my = target_wp
    draw.ellipse([mx-6, my-6, mx+6, my+6], fill=IRON_DARK, outline=IRON)
    # 尖刺
    for angle in [0, 90, 180, 270]:
        import math
        rad = math.radians(angle)
        px, py = mx + math.cos(rad)*8, my + math.sin(rad)*8
        draw.line([mx, my, px, py], fill=IRON)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    FRAME_SIZE = 64
    COLS = 4
    ROWS = 3
    
    # 创建画布
    sheet = Image.new('RGBA', (FRAME_SIZE * COLS, FRAME_SIZE * ROWS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    actions = [
        ("idle", 0),
        ("walk", 1),
        ("attack", 2)
    ]

    for action_name, row_idx in actions:
        for col_idx in range(COLS):
            x_offset = col_idx * FRAME_SIZE
            y_offset = row_idx * FRAME_SIZE
            draw_general(draw, x_offset, y_offset, action_name, col_idx)

    # 保存结果
    sheet.save(args.output)

if __name__ == "__main__":
    main()