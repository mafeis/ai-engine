import argparse
from PIL import Image, ImageDraw

def draw_tudigong(draw, ox, oy, action, frame_idx):
    """
    绘制土地公角色
    ox, oy: 帧的左上角原点
    action: 'idle', 'walk', 'attack'
    frame_idx: 0-3
    """
    # 基础颜色配置
    COLOR_ROBE = (46, 139, 87, 255)      # 绿叶服
    COLOR_SKIN = (255, 218, 185, 255)    # 肤色
    COLOR_BEARD = (240, 240, 240, 255)   # 胡须
    COLOR_STAFF = (101, 67, 33, 255)     # 木杖
    COLOR_PEACH = (255, 105, 180, 255)   # 仙桃
    COLOR_GLOW = (255, 255, 200, 150)    # 桃子光芒
    COLOR_EYE = (40, 40, 40, 255)        # 眯眯眼

    # 动画偏移逻辑
    bob = 0
    leg_l_off = 0
    leg_r_off = 0
    staff_angle = 0
    peach_glow_size = 0
    
    if action == 'idle':
        bob = [0, 2, 3, 1][frame_idx]
        staff_angle = [0, 1, 2, 1][frame_idx]
    elif action == 'walk':
        bob = [1, 0, 1, 0][frame_idx]
        leg_l_off = [0, -4, 0, 0][frame_idx]
        leg_r_off = [0, 0, 0, -4][frame_idx]
        staff_angle = frame_idx % 2
    elif action == 'attack':
        if frame_idx == 0: # 蓄力
            staff_angle = -5
            bob = 2
        elif frame_idx == 1: # 挥动
            staff_angle = 10
            bob = 0
            peach_glow_size = 6
        elif frame_idx == 2: # 命中/爆发
            staff_angle = 12
            bob = 0
            peach_glow_size = 12
        elif frame_idx == 3: # 收招
            staff_angle = 5
            bob = 1

    # 角色中心参考点 (32, 48)
    cx, cy = ox + 32, oy + 48 - bob

    # 1. 绘制腿部 (短小)
    draw.rectangle([cx-8, cy, cx-4, cy+4+leg_l_off], fill=COLOR_ROBE)
    draw.rectangle([cx+4, cy, cx+8, cy+4+leg_r_off], fill=COLOR_ROBE)

    # 2. 绘制身体 (绿叶袍)
    draw.ellipse([cx-14, cy-20, cx+14, cy+2], fill=COLOR_ROBE)
    
    # 3. 绘制胡须 (垂到地面)
    # 胡须随 bob 摆动
    beard_points = [cx-10, cy-12, cx+10, cy-12, cx+12, cy+12+bob, cx, cy+16+bob, cx-12, cy+12+bob]
    draw.polygon(beard_points, fill=COLOR_BEARD)

    # 4. 头部
    head_y = cy - 24
    draw.ellipse([cx-10, head_y-12, cx+10, head_y+8], fill=COLOR_SKIN)
    
    # 眯眯眼
    draw.line([cx-6, head_y-2, cx-2, head_y-2], fill=COLOR_EYE, width=1)
    draw.line([cx+2, head_y-2, cx+6, head_y-2], fill=COLOR_EYE, width=1)

    # 5. 木杖与仙桃
    staff_x = cx + 16 + (staff_angle * 1.5)
    staff_top_y = cy - 30 - (staff_angle * 2)
    # 绘制木杖
    draw.line([staff_x, cy+8, staff_x - 4, staff_top_y], fill=COLOR_STAFF, width=3)
    
    # 仙桃
    peach_x, peach_y = staff_x - 5, staff_top_y - 2
    if peach_glow_size > 0:
        draw.ellipse([peach_x-peach_glow_size, peach_y-peach_glow_size, 
                      peach_x+8+peach_glow_size, peach_y+8+peach_glow_size], fill=COLOR_GLOW)
    draw.ellipse([peach_x, peach_y, peach_x+8, peach_y+8], fill=COLOR_PEACH)
    # 桃尖
    draw.point([peach_x+4, peach_y-1], fill=COLOR_PEACH)

    # 6. 手臂 (简单示意)
    draw.line([cx+10, cy-10, staff_x-2, cy-8], fill=COLOR_ROBE, width=4)

def main():
    parser = argparse.ArgumentParser(description="Generate Tudigong Spritesheet")
    parser.add_argument('--output', required=True, help="Output path for the spritesheet PNG")
    args = parser.parse_args()

    # 配置参数
    frame_w, frame_h = 64, 64
    cols, rows = 4, 3
    actions = ['idle', 'walk', 'attack']

    # 创建画布
    canvas_w = frame_w * cols
    canvas_h = frame_h * rows
    spritesheet = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(spritesheet)

    # 循环绘制每一帧
    for row_idx, action in enumerate(actions):
        for col_idx in range(cols):
            x_offset = col_idx * frame_w
            y_offset = row_idx * frame_h
            draw_tudigong(draw, x_offset, y_offset, action, col_idx)

    # 保存结果
    spritesheet.save(args.output)
    print(f"Spritesheet successfully saved to {args.output}")

if __name__ == "__main__":
    main()