import argparse
from PIL import Image, ImageDraw

def draw_pixel_rect(draw, x, y, w, h, color):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)

def draw_npc_zhang_sun(draw, ox, oy, action, frame_idx):
    # Colors
    C_SKIN_Z = (180, 140, 100, 255)  # Zhang: Tan skin
    C_SKIN_S = (240, 200, 180, 255)  # Sun: Fair skin
    C_APRON = (60, 50, 40, 255)      # Greasy apron
    C_RED = (200, 20, 20, 255)       # Red tube top / Flower
    C_KNIFE = (160, 160, 170, 255)   # Steel
    C_HAIR = (30, 25, 20, 255)       # Dark hair
    C_PANTS = (40, 40, 60, 255)      # Dark pants

    # Animation offsets
    z_y_off = 0
    s_y_off = 0
    z_arm_ext = 0
    s_arm_ext = 0
    leg_phase = 0

    if action == "idle":
        # Breathing bobbing
        z_y_off = [0, 1, 2, 1][frame_idx % 4]
        s_y_off = [1, 0, 1, 2][frame_idx % 4]
    elif action == "walk":
        # Walking cycle
        z_y_off = [0, 1, 0, 1][frame_idx % 4]
        s_y_off = [1, 0, 1, 0][frame_idx % 4]
        leg_phase = frame_idx % 4
    elif action == "attack":
        # Attack sequence: Wind up -> Strike -> Follow through -> Recover
        if frame_idx == 0: z_arm_ext, s_arm_ext = -2, -2
        elif frame_idx == 1: z_arm_ext, s_arm_ext = 8, 6
        elif frame_idx == 2: z_arm_ext, s_arm_ext = 6, 4
        else: z_arm_ext, s_arm_ext = 0, 0

    # --- Draw Zhang Qing (Left) ---
    zx, zy = ox + 16, oy + 24 + z_y_off
    # Body & Apron
    draw_pixel_rect(draw, zx, zy, 14, 18, C_APRON) # Apron
    draw_pixel_rect(draw, zx+2, zy-8, 10, 10, C_SKIN_Z) # Head
    draw_pixel_rect(draw, zx+1, zy-9, 12, 4, C_HAIR) # Hair
    # Legs
    l_off = 4 if leg_phase == 1 else (0 if leg_phase == 3 else 2)
    draw_pixel_rect(draw, zx+2, zy+18, 4, 6 - (l_off//2), C_PANTS)
    draw_pixel_rect(draw, zx+8, zy+18, 4, 6 - ((4-l_off)//2), C_PANTS)
    # Kitchen Knife
    draw_pixel_rect(draw, zx+12+z_arm_ext, zy+4, 4, 8, C_KNIFE) # Blade
    draw_pixel_rect(draw, zx+10+z_arm_ext, zy+8, 4, 2, (80, 60, 40, 255)) # Handle

    # --- Draw Sun Erniang (Right) ---
    sx, sy = ox + 36, oy + 26 + s_y_off
    # Body & Red Top
    draw_pixel_rect(draw, sx, sy, 10, 14, C_RED) # Red tube top
    draw_pixel_rect(draw, sx+1, sy-8, 8, 8, C_SKIN_S) # Head
    draw_pixel_rect(draw, sx, sy-9, 10, 3, C_HAIR) # Hair
    draw_pixel_rect(draw, sx+7, sy-10, 4, 4, C_RED) # Big Red Flower
    # Legs
    l_off_s = 4 if leg_phase == 2 else (0 if leg_phase == 0 else 2)
    draw_pixel_rect(draw, sx+1, sy+14, 3, 6 - (l_off_s//2), C_SKIN_S)
    draw_pixel_rect(draw, sx+6, sy+14, 3, 6 - ((4-l_off_s)//2), C_SKIN_S)
    # Short Knives (Waist/Hands)
    if action == "attack" and frame_idx > 0:
        draw_pixel_rect(draw, sx+8+s_arm_ext, sy+2, 6, 2, C_KNIFE) # Knife 1
        draw_pixel_rect(draw, sx-4-s_arm_ext, sy+6, 6, 2, C_KNIFE) # Knife 2
    else:
        draw_pixel_rect(draw, sx-2, sy+8, 2, 6, C_KNIFE) # Tucked knife 1
        draw_pixel_rect(draw, sx+10, sy+8, 2, 6, C_KNIFE) # Tucked knife 2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, help="Path to save the spritesheet")
    args = parser.parse_args()

    frame_w, frame_h = 64, 64
    cols, rows = 4, 3
    actions = ["idle", "walk", "attack"]

    sheet = Image.new('RGBA', (frame_w * cols, frame_h * rows), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    for row_idx, action in enumerate(actions):
        for col_idx in range(cols):
            x_offset = col_idx * frame_w
            y_offset = row_idx * frame_h
            draw_npc_zhang_sun(draw, x_offset, y_offset, action, col_idx)

    # Apply a slight pixelated upscale effect if needed, but here we save raw
    sheet.save(args.output)

if __name__ == "__main__":
    main()