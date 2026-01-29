import argparse
from PIL import Image, ImageDraw

def draw_pixel_rect(draw, x, y, w, h, color):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)

def draw_xiaozuanfeng(draw, ox, oy, action, frame_idx):
    # Colors
    C_SKIN = (100, 160, 60, 255)      # Greenish demon
    C_HELMET = (60, 60, 70, 255)      # Dark iron
    C_HELMET_L = (80, 80, 90, 255)    # Helmet highlight
    C_CLOTH = (120, 70, 40, 255)      # Brown rags
    C_FLAG = (200, 30, 30, 255)       # Red flag
    C_POLE = (100, 80, 60, 255)       # Wooden pole
    C_GONG = (240, 190, 40, 255)      # Golden gong
    C_MALLET = (150, 150, 150, 255)   # Mallet head

    # Base coordinates (center of 64x64 is 32, 32)
    cx, cy = ox + 32, oy + 45
    
    # Animation offsets
    body_y = 0
    leg_l_y, leg_r_y = 0, 0
    arm_l_y, arm_r_y = 0, 0
    flag_angle = 0
    gong_shake = 0
    mallet_pos = (0, 0)

    if action == "idle":
        # Gentle breathing
        body_y = [0, -1, -2, -1][frame_idx % 4]
        flag_angle = [0, 2, 4, 2][frame_idx % 4]
        arm_r_y = body_y
        
    elif action == "walk":
        # Clumsy waddle
        body_y = [0, -2, 0, -2][frame_idx % 4]
        leg_l_y = [-4, 0, 0, 0][frame_idx % 4]
        leg_r_y = [0, 0, -4, 0][frame_idx % 4]
        flag_angle = [-5, 5, -5, 5][frame_idx % 4]
        arm_l_y = body_y + 1
        arm_r_y = body_y - 1

    elif action == "attack":
        # Hit the gong
        if frame_idx == 0: # Wind up
            mallet_pos = (-2, -8)
            body_y = 1
        elif frame_idx == 1: # Strike
            mallet_pos = (6, 2)
            gong_shake = 2
            body_y = -1
        elif frame_idx == 2: # Impact
            mallet_pos = (5, 3)
            gong_shake = -2
            # Draw sound waves
            draw_pixel_rect(draw, cx+15, cy-15, 2, 2, (255, 255, 255, 150))
            draw_pixel_rect(draw, cx+18, cy-10, 2, 2, (255, 255, 255, 150))
        else: # Recover
            mallet_pos = (0, 0)
            body_y = 0

    # 1. Draw Flag (Behind)
    fx, fy = cx - 8, cy - 15 + body_y
    draw_pixel_rect(draw, fx, fy - 15, 2, 20, C_POLE) # Pole
    flag_pts = [
        (fx - 12 + flag_angle, fy - 15), 
        (fx, fy - 12), 
        (fx, fy - 5), 
        (fx - 12 + flag_angle, fy - 8)
    ]
    draw.polygon(flag_pts, fill=C_FLAG)

    # 2. Draw Legs
    draw_pixel_rect(draw, cx - 6, cy + leg_l_y, 4, 5, C_SKIN) # Left
    draw_pixel_rect(draw, cx + 2, cy + leg_r_y, 4, 5, C_SKIN) # Right

    # 3. Draw Body
    draw_pixel_rect(draw, cx - 8, cy - 12 + body_y, 16, 14, C_CLOTH)
    draw_pixel_rect(draw, cx - 6, cy - 10 + body_y, 12, 10, C_SKIN)

    # 4. Draw Gong (Left Hand)
    gx, gy = cx + 8 + gong_shake, cy - 5 + arm_l_y
    draw_pixel_rect(draw, gx, gy, 10, 10, C_GONG)
    draw_pixel_rect(draw, gx + 2, gy + 2, 6, 6, (200, 150, 0, 255)) # Gong center

    # 5. Draw Mallet (Right Hand)
    mx, my = cx - 12 + mallet_pos[0], cy - 2 + arm_r_y + mallet_pos[1]
    draw_pixel_rect(draw, mx, my, 6, 2, C_POLE)
    draw_pixel_rect(draw, mx - 2, my - 1, 3, 4, C_MALLET)

    # 6. Draw Oversized Helmet (Covers eyes)
    hx, hy = cx - 14, cy - 28 + body_y
    draw_pixel_rect(draw, hx, hy, 28, 18, C_HELMET)
    draw_pixel_rect(draw, hx + 2, hy + 2, 24, 4, C_HELMET_L) # Top shine
    # Helmet Horns/Spikes
    draw_pixel_rect(draw, hx + 4, hy - 4, 4, 4, C_HELMET)
    draw_pixel_rect(draw, hx + 20, hy - 4, 4, 4, C_HELMET)
    # Nose peeking out
    draw_pixel_rect(draw, cx - 2, cy - 12 + body_y, 4, 3, C_SKIN)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Output path for the spritesheet")
    args = parser.parse_args()

    fw, fh = 64, 64
    cols, rows = 4, 3
    sheet = Image.new('RGBA', (fw * cols, fh * rows), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    actions = ["idle", "walk", "attack"]

    for row, action in enumerate(actions):
        for col in range(cols):
            ox = col * fw
            oy = row * fh
            draw_xiaozuanfeng(draw, ox, oy, action, col)

    # Apply a slight pixelated scaling effect if desired, 
    # but here we stay true to the 64x64 grid as requested.
    sheet.save(args.output)

if __name__ == "__main__":
    main()