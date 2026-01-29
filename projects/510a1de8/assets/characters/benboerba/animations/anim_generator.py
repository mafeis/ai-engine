import argparse
from PIL import Image, ImageDraw

def draw_benboerba(draw, ox, oy, action, frame_idx):
    """
    绘制奔波儿灞 (Benboerba) 角色帧
    ox, oy: 帧左上角坐标
    action: 'idle', 'walk', 'attack'
    frame_idx: 0-3
    """
    # 基础颜色定义
    COLOR_SKIN = (100, 180, 255, 255)      # 浅蓝色鱼皮
    COLOR_SKIN_DARK = (70, 140, 220, 255) # 深蓝色鳞片
    COLOR_EYE_WHITE = (255, 255, 255, 255)
    COLOR_EYE_PUPIL = (0, 0, 0, 255)
    COLOR_ARMOR = (46, 139, 87, 255)      # 海藻绿
    COLOR_TRIDENT = (192, 192, 192, 255)  # 银色三叉戟
    COLOR_TRIDENT_SHAFT = (139, 69, 19, 255) # 木质柄
    COLOR_BUBBLE = (200, 240, 255, 180)   # 半透明气泡

    # 动画偏移逻辑
    body_y_offset = 0
    arm_swing = 0
    leg_pos = 0
    weapon_ext = 0
    bubble_size = 0

    if action == 'idle':
        # 呼吸效果：上下微动
        body_y_offset = [0, 1, 2, 1][frame_idx]
    elif action == 'walk':
        # 行走效果：腿部交替，身体轻微晃动
        leg_pos = [2, 0, -2, 0][frame_idx]
        body_y_offset = [0, 1, 0, 1][frame_idx]
        arm_swing = leg_pos * 1.5
    elif action == 'attack':
        # 攻击效果：蓄力 -> 刺出 -> 气泡 -> 收招
        weapon_ext = [-2, 8, 12, 4][frame_idx]
        bubble_size = [0, 0, 10, 5][frame_idx]
        body_y_offset = [0, 0, 0, 0][frame_idx]

    # 中心参考点 (32, 40)
    cx, cy = ox + 32, oy + 40 + body_y_offset

    # 1. 绘制腿部 (Legs)
    if action == 'walk':
        draw.rectangle([cx-8+leg_pos, cy+8, cx-4+leg_pos, cy+16], fill=COLOR_SKIN) # 左腿
        draw.rectangle([cx+4-leg_pos, cy+8, cx+8-leg_pos, cy+16], fill=COLOR_SKIN) # 右腿
    else:
        draw.rectangle([cx-8, cy+8, cx-4, cy+16], fill=COLOR_SKIN)
        draw.rectangle([cx+4, cy+8, cx+8, cy+16], fill=COLOR_SKIN)

    # 2. 绘制身体 (Body)
    draw.ellipse([cx-12, cy-10, cx+12, cy+10], fill=COLOR_SKIN)
    # 鳞片细节
    draw.point([(cx-4, cy-2), (cx+4, cy+2), (cx, cy+5)], fill=COLOR_SKIN_DARK)
    
    # 3. 绘制海藻盔甲 (Seaweed Armor)
    draw.rectangle([cx-13, cy-2, cx+13, cy+4], fill=COLOR_ARMOR)
    draw.rectangle([cx-6, cy-10, cx-2, cy+4], fill=COLOR_ARMOR)
    draw.rectangle([cx+2, cy-10, cx+6, cy+4], fill=COLOR_ARMOR)

    # 4. 绘制头部 (Head)
    head_y = cy - 18
    draw.ellipse([cx-14, head_y-12, cx+14, head_y+10], fill=COLOR_SKIN)
    
    # 5. 绘制大眼睛 (Bulging Eyes)
    # 左眼
    draw.ellipse([cx-16, head_y-8, cx-4, head_y+4], fill=COLOR_EYE_WHITE)
    draw.ellipse([cx-12, head_y-4, cx-8, head_y], fill=COLOR_EYE_PUPIL)
    # 右眼
    draw.ellipse([cx+4, head_y-8, cx+16, head_y+4], fill=COLOR_EYE_WHITE)
    draw.ellipse([cx+8, head_y-4, cx+12, head_y], fill=COLOR_EYE_PUPIL)

    # 6. 绘制手臂与武器 (Arm & Weapon)
    arm_x = cx + 12 + arm_swing
    arm_y = cy - 2
    
    if action == 'attack':
        # 攻击时手臂前伸
        wx = arm_x + weapon_ext
        wy = arm_y
        # 绘制手臂
        draw.line([cx+8, cy, wx, wy], fill=COLOR_SKIN, width=4)
        # 绘制三叉戟柄
        draw.line([wx, wy, wx+15, wy], fill=COLOR_TRIDENT_SHAFT, width=2)
        # 绘制三叉戟头
        draw.polygon([(wx+15, wy-6), (wx+22, wy), (wx+15, wy+6)], fill=COLOR_TRIDENT)
        # 绘制气泡
        if bubble_size > 0:
            draw.ellipse([wx+25, wy-bubble_size, wx+25+bubble_size*2, wy+bubble_size], outline=COLOR_BUBBLE, width=1)
    else:
        # 平时斜握
        wx, wy = arm_x + 5, arm_y - 5
        draw.line([cx+8, cy, wx, wy], fill=COLOR_SKIN, width=4)
        draw.line([wx-5, wy+15, wx+10, wy-10], fill=COLOR_TRIDENT_SHAFT, width=2)
        draw.polygon([(wx+8, wy-12), (wx+15, wy-18), (wx+18, wy-8)], fill=COLOR_TRIDENT)

    # 7. 鱼鳍 (Fins)
    draw.polygon([(cx-14, head_y), (cx-20, head_y-5), (cx-14, head_y-10)], fill=COLOR_SKIN_DARK)
    draw.polygon([(cx+14, head_y), (cx+20, head_y-5), (cx+14, head_y-10)], fill=COLOR_SKIN_DARK)

def main():
    parser = argparse.ArgumentParser(description="Generate Benboerba Spritesheet")
    parser.add_argument('--output', required=True, help="Output image path (e.g. benboerba_sheet.png)")
    args = parser.parse_args()

    FRAME_W = 64
    FRAME_H = 64
    COLS = 4
    ROWS = 3
    
    # 创建画布
    sheet = Image.new('RGBA', (FRAME_W * COLS, FRAME_H * ROWS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    actions = ['idle', 'walk', 'attack']

    for row_idx, action in enumerate(actions):
        for col_idx in range(COLS):
            x_offset = col_idx * FRAME_W
            y_offset = row_idx * FRAME_H
            draw_benboerba(draw, x_offset, y_offset, action, col_idx)

    # 保存结果
    sheet.save(args.output)
    print(f"Spritesheet successfully saved to {args.output}")

if __name__ == "__main__":
    main()