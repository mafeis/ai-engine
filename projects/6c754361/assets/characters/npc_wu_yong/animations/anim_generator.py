import argparse
from PIL import Image, ImageDraw

def draw_frame(draw, x_offset, y_offset, action, frame_idx):
    """
    绘制 NPC 吴用的单帧像素图像
    """
    # 基础颜色定义
    COLOR_ROBE = (100, 149, 237, 255)      # 蓝衫
    COLOR_ROBE_DARK = (70, 110, 180, 255)
    COLOR_SKIN = (255, 224, 189, 255)      # 肤色
    COLOR_HAT = (40, 40, 60, 255)          # 纶巾
    COLOR_BEARD = (30, 30, 30, 255)        # 胡须
    COLOR_FAN = (245, 245, 245, 255)       # 羽扇
    COLOR_EYE = (0, 0, 0, 255)             # 眼睛
    COLOR_SPARKLE = (255, 255, 255, 255)   # 闪烁光点

    # 动画参数计算
    bob = 0
    leg_l_y, leg_r_y = 0, 0
    fan_angle = 0
    fan_x_off, fan_y_off = 0, 0
    sparkle_alpha = 0

    if action == "idle":
        # 呼吸起伏
        bob = [0, 1, 2, 1][frame_idx % 4]
        fan_x_off = [0, 1, 2, 1][frame_idx % 4]
        sparkle_alpha = [100, 255, 150, 200][frame_idx % 4]
    
    elif action == "walk":
        # 行走摆动
        bob = [0, 1, 0, 1][frame_idx % 4]
        leg_l_y = [0, -4, 0, 0][frame_idx % 4]
        leg_r_y = [0, 0, 0, -4][frame_idx % 4]
        fan_x_off = [0, 2, 0, 2][frame_idx % 4]
        sparkle_alpha = 180

    elif action == "attack":
        # 攻击动作：蓄力 -> 挥扇 -> 释放 -> 收招
        if frame_idx == 0: # 蓄力
            fan_x_off, fan_y_off = -4, -2
            bob = 0
        elif frame_idx == 1: # 挥动
            fan_x_off, fan_y_off = 8, 4
            bob = 2
        elif frame_idx == 2: # 释放
            fan_x_off, fan_y_off = 12, 2
            bob = 1
            sparkle_alpha = 255
        else: # 收招
            fan_x_off, fan_y_off = 4, 0
            bob = 0

    # 角色中心基准坐标
    cx, cy = x_offset + 32, y_offset + 32 + bob

    # 1. 绘制腿部/鞋子
    draw.rectangle([cx-8, y_offset+52+leg_l_y, cx-2, y_offset+60+leg_l_y], fill=COLOR_ROBE_DARK)
    draw.rectangle([cx+2, y_offset+52+leg_r_y, cx+8, y_offset+60+leg_r_y], fill=COLOR_ROBE_DARK)

    # 2. 绘制身体 (长衫)
    draw.rectangle([cx-10, cy-4, cx+10, cy+20], fill=COLOR_ROBE)
    draw.rectangle([cx-11, cy+10, cx+11, cy+22], fill=COLOR_ROBE) # 裙摆微宽

    # 3. 绘制头部
    draw.rectangle([cx-7, cy-18, cx+7, cy-4], fill=COLOR_SKIN)
    
    # 纶巾 (帽子)
    draw.polygon([(cx-8, cy-18), (cx+8, cy-18), (cx+6, cy-26), (cx-6, cy-26)], fill=COLOR_HAT)
    draw.rectangle([cx-2, cy-28, cx+2, cy-24], fill=COLOR_HAT) # 巾顶

    # 眼睛 (精明的小眼)
    draw.point([(cx-3, cy-12), (cx+3, cy-12)], fill=COLOR_EYE)

    # 三绺长须
    draw.line([(cx-4, cy-4), (cx-4, cy+4)], fill=COLOR_BEARD, width=1) # 左
    draw.line([(cx, cy-4), (cx, cy+6)], fill=COLOR_BEARD, width=1)    # 中
    draw.line([(cx+4, cy-4), (cx+4, cy+4)], fill=COLOR_BEARD, width=1) # 右

    # 4. 绘制手臂与羽扇
    hand_x, hand_y = cx + 10, cy + 4
    if action == "attack":
        hand_x += fan_x_off
        hand_y += fan_y_off
    
    # 手臂
    draw.line([(cx+4, cy+2), (hand_x, hand_y)], fill=COLOR_ROBE, width=3)
    
    # 羽扇 (半圆形像素组)
    fan_base_x, fan_base_y = hand_x + 2, hand_y - 4
    draw.chord([fan_base_x-8, fan_base_y-10, fan_base_x+8, fan_base_y+2], 180, 360, fill=COLOR_FAN)
    # 扇柄
    draw.line([(fan_base_x, fan_base_y), (fan_base_x, fan_base_y+4)], fill=(139, 69, 19, 255), width=1)

    # 5. 绘制闪烁光点 (羽扇特效)
    if sparkle_alpha > 0:
        s_color = (255, 255, 255, sparkle_alpha)
        offsets = [(-4, -6), (2, -8), (-1, -4)]
        if action == "attack" and frame_idx == 2: # 攻击时光点飞散
            offsets = [(10, -2), (15, 2), (12, 6)]
        
        for ox, oy in offsets:
            px, py = fan_base_x + ox, fan_base_y + oy
            draw.point([(px, py)], fill=s_color)
            # 十字星芒
            if sparkle_alpha > 200:
                draw.point([(px-1, py), (px+1, py), (px, py-1), (px, py+1)], fill=s_color)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    frame_w, frame_h = 64, 64
    cols, rows = 4, 3
    actions = ["idle", "walk", "attack"]

    # 创建画布
    sheet = Image.new('RGBA', (frame_w * cols, frame_h * rows), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    for row_idx, action in enumerate(actions):
        for col_idx in range(cols):
            x = col_idx * frame_w
            y = row_idx * frame_h
            draw_frame(draw, x, y, action, col_idx)

    # 保存结果
    sheet.save(args.output)

if __name__ == "__main__":
    main()