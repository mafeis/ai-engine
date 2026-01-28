import argparse
from PIL import Image, ImageDraw

def draw_character(draw, ox, oy, action, frame_idx):
    """
    ox, oy: 帧的左上角坐标
    action: 0-Idle, 1-Walk, 2-Attack
    frame_idx: 0-3
    """
    # 颜色定义
    SKIN = (85, 55, 40)        # 矮黑肤色
    ROBE = (100, 40, 120)      # 紫色官服
    ROBE_LIGHT = (130, 60, 150)
    BOOK = (230, 220, 150)     # 泛黄天书
    CLOUD = (200, 150, 255, 160) # 紫色云团
    BLACK = (20, 20, 20)       # 官帽/眼睛
    
    # 基础偏移
    bx, by = ox + 32, oy + 45
    
    # 动画参数计算
    bob = 0
    leg_l, leg_r = 0, 0
    arm_y = 0
    book_pos = [bx + 8, by - 12]
    cloud_scale = 0
    
    if action == 0: # Idle: 呼吸起伏
        bob = [0, 1, 2, 1][frame_idx]
        cloud_scale = frame_idx % 2
    elif action == 1: # Walk: 腿部摆动
        bob = [0, 2, 0, 2][frame_idx]
        leg_l = [-4, 0, 4, 0][frame_idx]
        leg_r = [4, 0, -4, 0][frame_idx]
        arm_y = bob
    elif action == 2: # Attack: 举书施法
        if frame_idx == 0: # 蓄力
            bob = 2
            book_pos = [bx + 8, by - 8]
        elif frame_idx == 1: # 举起
            bob = 0
            book_pos = [bx + 10, by - 25]
            cloud_scale = 3
        elif frame_idx == 2: # 爆发
            bob = 0
            book_pos = [bx + 12, by - 30]
            cloud_scale = 6
            # 施法光效
            draw.ellipse([bx-15, by-45, bx+35, by+5], fill=(255, 255, 255, 100))
        elif frame_idx == 3: # 收招
            bob = 1
            book_pos = [bx + 8, by - 15]

    # 1. 绘制云团 (背景层)
    c_size = 10 + cloud_scale
    draw.ellipse([bx-15-c_size, oy+5-c_size//2, bx+15+c_size, oy+15+c_size//2], fill=CLOUD)

    # 2. 绘制腿部
    draw.rectangle([bx-8, by-5+leg_l, bx-2, by+5], fill=ROBE) # 左腿
    draw.rectangle([bx+2, by-5+leg_r, bx+8, by+5], fill=ROBE) # 右腿

    # 3. 绘制身体 (官服)
    body_rect = [bx-12, by-25+bob, bx+12, by-2]
    draw.rectangle(body_rect, fill=ROBE)
    # 破损细节 (深色色块)
    draw.point([(bx-5, by-15+bob), (bx+4, by-10+bob), (bx-2, by-20+bob)], fill=(60, 20, 80))

    # 4. 绘制头部
    head_y = by-35+bob
    draw.ellipse([bx-10, head_y, bx+10, head_y+15], fill=SKIN)
    # 官帽
    draw.rectangle([bx-12, head_y-2, bx+12, head_y+3], fill=BLACK)
    draw.rectangle([bx-6, head_y-8, bx+6, head_y-2], fill=BLACK)
    # 眼睛 (和善的眯眯眼)
    draw.line([bx-5, head_y+7, bx-2, head_y+7], fill=BLACK)
    draw.line([bx+2, head_y+7, bx+5, head_y+7], fill=BLACK)

    # 5. 绘制手臂与天书
    # 左手 (垂下)
    draw.rectangle([bx-15, by-20+bob+arm_y, bx-10, by-10+bob+arm_y], fill=ROBE)
    # 右手与天书
    draw.rectangle([bx+10, book_pos[1]+5, bx+15, book_pos[1]+12], fill=SKIN) # 手
    # 天书
    draw.rectangle([book_pos[0], book_pos[1], book_pos[0]+10, book_pos[1]+14], fill=BOOK)
    draw.line([book_pos[0]+2, book_pos[1]+3, book_pos[0]+8, book_pos[1]+3], fill=(100, 80, 40)) # 书纹
    draw.line([book_pos[0]+2, book_pos[1]+7, book_pos[0]+8, book_pos[1]+7], fill=(100, 80, 40))
    draw.line([book_pos[0]+2, book_pos[1]+11, book_pos[0]+8, book_pos[1]+11], fill=(100, 80, 40))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    frame_w, frame_h = 64, 64
    cols, rows = 4, 3
    
    # 创建画布
    sheet = Image.new('RGBA', (frame_w * cols, frame_h * rows), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    # 动作列表: 0=Idle, 1=Walk, 2=Attack
    for row in range(rows):
        for col in range(cols):
            x_offset = col * frame_w
            y_offset = row * frame_h
            draw_character(draw, x_offset, y_offset, row, col)

    # 保存结果
    sheet.save(args.output)

if __name__ == "__main__":
    main()