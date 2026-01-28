import argparse
from PIL import Image, ImageDraw

def draw_minion(draw, ox, oy, action, frame_idx):
    """
    绘制 enemy_minion 角色
    ox, oy: 帧的左上角坐标
    action: 0: Idle, 1: Walk, 2: Attack
    frame_idx: 0-3
    """
    # 基础颜色
    COLOR_CLOTH = (139, 0, 0, 255)      # 暗红色官服
    COLOR_HAT = (20, 20, 20, 255)        # 黑帽子
    COLOR_SKIN = (245, 222, 179, 255)    # 皮肤
    COLOR_EYE = (0, 0, 0, 255)           # 眯眯眼
    COLOR_SPEAR_SHAFT = (101, 67, 33, 255) # 矛柄
    COLOR_SPEAR_TIP = (169, 169, 169, 255) # 锈铁色
    COLOR_RUST = (183, 65, 14, 255)      # 锈迹

    # 动画偏移逻辑
    bob = 0
    leg_offset = 0
    spear_x_off = 0
    spear_y_off = 0
    lean = 0

    if action == 0:  # Idle: 呼吸起伏
        bob = [0, 1, 2, 1][frame_idx]
    elif action == 1:  # Walk: 腿部摆动与身体颠簸
        bob = [0, 2, 0, 2][frame_idx]
        leg_offset = [-3, 0, 3, 0][frame_idx]
    elif action == 2:  # Attack: 蓄力与刺出
        if frame_idx == 0: # 蓄力
            lean = -2
            spear_x_off = -4
        elif frame_idx == 1: # 刺出
            lean = 4
            spear_x_off = 12
        elif frame_idx == 2: # 延伸
            lean = 2
            spear_x_off = 16
        elif frame_idx == 3: # 收招
            lean = 0
            spear_x_off = 4

    # 角色中心参考点 (32, 40)
    cx, cy = ox + 32, oy + 40 + bob

    # 1. 绘制腿部
    if action == 1: # 行走时的腿
        draw.rectangle([cx-6+leg_offset, cy+10, cx-2+leg_offset, cy+18], fill=COLOR_CLOTH)
        draw.rectangle([cx+2-leg_offset, cy+10, cx+6-leg_offset, cy+18], fill=COLOR_CLOTH)
    else: # 站立时的腿
        draw.rectangle([cx-6, cy+10, cx-2, cy+18], fill=COLOR_CLOTH)
        draw.rectangle([cx+2, cy+10, cx+6, cy+18], fill=COLOR_CLOTH)

    # 2. 绘制身体 (官服)
    body_rect = [cx-10 + lean, cy-10, cx+10 + lean, cy+12]
    draw.rectangle(body_rect, fill=COLOR_CLOTH)
    # 官服细节 (黄色纽扣/装饰)
    draw.point([(cx+lean, cy), (cx+lean, cy+4)], fill=(218, 165, 32, 255))

    # 3. 绘制头部
    head_y = cy - 22
    draw.rectangle([cx-7+lean, head_y, cx+7+lean, head_y+12], fill=COLOR_SKIN)
    
    # 眯眯眼 (猥琐表情)
    draw.line([cx+1+lean, head_y+5, cx+5+lean, head_y+5], fill=COLOR_EYE, width=1)
    draw.line([cx-5+lean, head_y+5, cx-1+lean, head_y+5], fill=COLOR_EYE, width=1)
    # 猥琐的小胡子/嘴巴
    draw.point([(cx+lean, head_y+9), (cx-1+lean, head_y+10), (cx+1+lean, head_y+10)], fill=(50, 30, 0, 255))

    # 4. 歪斜的黑帽子
    draw.rectangle([cx-9+lean, head_y-4, cx+9+lean, head_y], fill=COLOR_HAT)
    draw.rectangle([cx-5+lean, head_y-10, cx+7+lean, head_y-4], fill=COLOR_HAT) # 歪向一侧

    # 5. 手臂与长矛
    arm_x = cx + 8 + lean
    arm_y = cy + 2
    # 绘制手臂
    draw.rectangle([arm_x, arm_y, arm_x+6, arm_y+4], fill=COLOR_CLOTH)
    
    # 绘制长矛
    sx = arm_x + 4 + spear_x_off
    sy = arm_y - 10 + spear_y_off
    # 矛柄
    draw.rectangle([sx, sy, sx+2, sy+30], fill=COLOR_SPEAR_SHAFT)
    # 矛头
    draw.polygon([(sx-2, sy), (sx+4, sy), (sx+1, sy-8)], fill=COLOR_SPEAR_TIP)
    # 锈迹
    draw.point([(sx+1, sy-4), (sx, sy-2)], fill=COLOR_RUST)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    frame_w, frame_h = 64, 64
    cols, rows = 4, 3
    
    # 创建画布
    sheet = Image.new('RGBA', (frame_w * cols, frame_h * rows), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    # 动作定义: 0:Idle, 1:Walk, 2:Attack
    for row in range(rows):
        for col in range(cols):
            draw_minion(draw, col * frame_w, row * frame_h, row, col)

    # 保存结果
    sheet.save(args.output)

if __name__ == "__main__":
    main()