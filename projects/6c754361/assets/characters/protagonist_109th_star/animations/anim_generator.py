import argparse
import random
from PIL import Image, ImageDraw

def draw_character(draw, ox, oy, action, frame, colors):
    """
    在指定位置绘制角色帧
    ox, oy: 帧的左上角原点
    action: 0-Idle, 1-Walk, 2-Attack
    frame: 0-3 帧索引
    """
    # 基础偏移量，用于模拟呼吸或动作起伏
    bob = 0
    arm_swing = 0
    leg_pos = 0
    attack_ext = 0
    
    if action == 0: # Idle
        bob = 1 if frame % 2 == 0 else 0
    elif action == 1: # Walk
        bob = frame % 2
        leg_pos = (frame % 4) - 2 # -2, -1, 0, 1 模拟迈步
        arm_swing = -leg_pos
    elif action == 2: # Attack
        if frame == 0: bob = 2 # 蓄力下蹲
        if frame == 1: attack_ext = 8 # 出招
        if frame == 2: attack_ext = 4 # 收招
        if frame == 3: bob = 0 # 回正

    # 中心参考点 (32, 32)
    cx, cy = ox + 32, oy + 48 + bob
    
    # 1. 绘制腿部与草鞋
    # 左腿
    lx = cx - 6 + (leg_pos * 2 if action == 1 else 0)
    draw.rectangle([lx-3, cy-12, lx+1, cy], fill=colors['pants']) # 裤子
    draw.rectangle([lx-3, cy-6, lx+1, cy-4], fill=colors['talisman']) # 符纸
    draw.rectangle([lx-4, cy, lx+2, cy+2], fill=colors['sandals']) # 草鞋
    
    # 右腿
    rx = cx + 4 - (leg_pos * 2 if action == 1 else 0)
    draw.rectangle([rx-1, cy-12, rx+3, cy], fill=colors['pants'])
    draw.rectangle([rx-1, cy-6, rx+3, cy-4], fill=colors['talisman'])
    draw.rectangle([rx-2, cy, rx+4, cy+2], fill=colors['sandals'])

    # 2. 身体 (交领长袍 + 短褐)
    body_top = cy - 28
    draw.rectangle([cx-8, body_top, cx+8, cy-10], fill=colors['robe']) # 内层米色
    draw.rectangle([cx-9, body_top, cx+9, cy-16], fill=colors['tunic']) # 外层深蓝
    # 腰带与星盘
    draw.line([cx-9, cy-14, cx+9, cy-14], fill=colors['belt'], width=3)
    draw.ellipse([cx+4, cy-15, cx+8, cy-11], fill=colors['gold'], outline=colors['belt']) # 天命星盘

    # 3. 手臂
    if action == 2 and frame == 1: # 攻击瞬间
        draw.rectangle([cx+8, body_top+4, cx+8+attack_ext, body_top+8], fill=colors['robe'])
        draw.point([cx+9+attack_ext, body_top+6], fill=colors['gold']) # 攻击特效
    else:
        # 左臂
        l_arm_y = body_top + 4 + (arm_swing if action == 1 else 0)
        draw.rectangle([cx-12, body_top+2, cx-8, l_arm_y+6], fill=colors['tunic'])
        # 右臂
        r_arm_y = body_top + 4 - (arm_swing if action == 1 else 0)
        draw.rectangle([cx+8, body_top+2, cx+12, r_arm_y+6], fill=colors['tunic'])

    # 4. 头部
    hx, hy = cx, body_top - 14
    # 头发与发髻
    draw.ellipse([hx-8, hy-10, hx+8, hy+6], fill=colors['hair'])
    draw.rectangle([hx-3, hy-14, hx+3, hy-8], fill=colors['hair']) # 发髻
    # 脸部
    draw.rectangle([hx-6, hy-4, hx+6, hy+6], fill=colors['skin'])
    # 抹额 (青色北斗七星)
    draw.line([hx-7, hy-2, hx+7, hy-2], fill=colors['cyan'], width=2)
    for i in range(3): # 简化北斗七星点
        draw.point([hx-4+i*3, hy-2], fill=colors['white'])
    # 眼睛
    draw.point([hx-3, hy+1], fill=colors['hair'])
    draw.point([hx+3, hy+1], fill=colors['hair'])

    # 5. 金色像素粒子 (随机升起)
    for _ in range(5):
        px = cx + random.randint(-15, 15)
        py = cy - random.randint(0, 40)
        draw.point([px, py], fill=colors['gold'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    # 定义调色板
    colors = {
        'hair': (34, 34, 34, 255),
        'skin': (255, 219, 172, 255),
        'cyan': (0, 255, 255, 255),
        'robe': (245, 245, 220, 255),
        'tunic': (25, 25, 112, 255),
        'belt': (139, 69, 19, 255),
        'pants': (17, 17, 17, 255),
        'talisman': (255, 215, 0, 255),
        'sandals': (180, 160, 120, 255),
        'gold': (255, 223, 0, 255),
        'white': (255, 255, 255, 255)
    }

    fw, fh = 64, 64
    cols, rows = 4, 3
    sheet = Image.new('RGBA', (fw * cols, fh * rows), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    for row_idx, action_name in enumerate(['Idle', 'Walk', 'Attack']):
        for col_idx in range(cols):
            x_offset = col_idx * fw
            y_offset = row_idx * fh
            draw_character(draw, x_offset, y_offset, row_idx, col_idx, colors)

    # 导出
    sheet.save(args.output)

if __name__ == "__main__":
    main()