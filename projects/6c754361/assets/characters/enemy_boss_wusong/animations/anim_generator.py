import argparse
from PIL import Image, ImageDraw

def draw_pixel_character(draw, ox, oy, action, frame, colors):
    """
    在指定位置绘制像素风武松
    ox, oy: 帧起始坐标
    action: 0-Idle, 1-Walk, 2-Attack
    frame: 0-3 帧索引
    """
    # 基础偏移与动画逻辑
    body_y_offset = 0
    arm_l_pos = [0, 0]
    arm_r_pos = [0, 0]
    leg_l_pos = [0, 0]
    leg_r_pos = [0, 0]
    saber_angle = 0
    eye_fire_size = frame % 3
    
    if action == 0: # Idle: 呼吸起伏
        body_y_offset = [0, 1, 2, 1][frame]
    elif action == 1: # Walk: 肢体交替
        body_y_offset = [0, 1, 0, 1][frame]
        leg_l_pos[1] = [-4, 0, 4, 0][frame]
        leg_r_pos[1] = [4, 0, -4, 0][frame]
        arm_l_pos[1] = [2, 0, -2, 0][frame]
        arm_r_pos[1] = [-2, 0, 2, 0][frame]
    elif action == 2: # Attack: 蓄力挥砍
        if frame == 0: # 蓄力
            body_y_offset = 2
            arm_l_pos = [-4, -2]
            arm_r_pos = [-4, -2]
        elif frame == 1: # 挥出
            body_y_offset = 0
            arm_l_pos = [8, 4]
            arm_r_pos = [8, 4]
            saber_angle = 45
        elif frame == 2: # 延伸
            body_y_offset = 0
            arm_l_pos = [12, 2]
            arm_r_pos = [12, 2]
            saber_angle = 90
        elif frame == 3: # 收招
            body_y_offset = 1
            arm_l_pos = [4, 0]
            arm_r_pos = [4, 0]

    # 核心坐标 (以64x64中心为基准)
    cx, cy = ox + 32, oy + 32 + body_y_offset
    
    # 1. 绘制腿部
    draw.rectangle([cx-8+leg_l_pos[0], cy+10+leg_l_pos[1], cx-2+leg_l_pos[0], cy+22], fill=colors['pants']) # 左腿
    draw.rectangle([cx+2+leg_r_pos[0], cy+10+leg_r_pos[1], cx+8+leg_r_pos[0], cy+22], fill=colors['pants']) # 右腿

    # 2. 绘制躯干 (肌肉夸张)
    draw.rectangle([cx-10, cy-10, cx+10, cy+12], fill=colors['skin']) # 胸腹
    # 纹身细节 (橙色点缀)
    draw.point([(cx-4, cy-2), (cx-3, cy-1), (cx-5, cy+1), (cx+2, cy-4)], fill=colors['tattoo'])

    # 3. 绘制头部
    draw.rectangle([cx-6, cy-22, cx+6, cy-10], fill=colors['skin']) # 脸
    draw.rectangle([cx-6, cy-24, cx+6, cy-20], fill=colors['hair']) # 头发/发带
    # 紫火眼睛
    draw.rectangle([cx-4-eye_fire_size//2, cy-18-eye_fire_size, cx-2, cy-16], fill=colors['fire'])
    draw.rectangle([cx+2, cy-18-eye_fire_size, cx+4+eye_fire_size//2, cy-16], fill=colors['fire'])

    # 4. 绘制手臂与戒刀
    for side in [-1, 1]: # -1左, 1右
        ax = cx + (12 * side) + (arm_l_pos[0] if side == -1 else arm_r_pos[0])
        ay = cy + (arm_l_pos[1] if side == -1 else arm_r_pos[1])
        
        # 手臂
        draw.rectangle([ax-3, ay-2, ax+3, ay+8], fill=colors['skin'])
        
        # 戒刀 (黑气缭绕)
        s_off = 10 * side
        draw.line([ax, ay+4, ax+s_off, ay+4+saber_angle//5], fill=colors['saber'], width=3)
        # 黑气特效
        if action == 2 and frame > 0:
            draw.ellipse([ax+s_off-4, ay-2, ax+s_off+4, ay+10], outline=colors['mist'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    # 配置
    FW, FH = 64, 64
    COLS, ROWS = 4, 3
    
    colors = {
        'skin': (210, 160, 130, 255),   # 肤色
        'pants': (40, 40, 45, 255),     # 深色裤子
        'hair': (20, 20, 20, 255),      # 黑发
        'fire': (180, 50, 255, 255),    # 紫火
        'tattoo': (200, 80, 0, 255),    # 虎纹
        'saber': (30, 30, 35, 255),     # 戒刀
        'mist': (60, 0, 80, 150)        # 黑紫气
    }

    # 创建画布
    sheet = Image.new('RGBA', (FW * COLS, FH * ROWS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    # 绘制动作行
    actions = ["Idle", "Walk", "Attack"]
    for row in range(ROWS):
        for col in range(COLS):
            draw_pixel_character(draw, col * FW, row * FH, row, col, colors)

    # 保存结果
    sheet.save(args.output)

if __name__ == "__main__":
    main()