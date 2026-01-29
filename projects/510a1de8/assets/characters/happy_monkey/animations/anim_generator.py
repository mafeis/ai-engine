import argparse
import math
from PIL import Image, ImageDraw

def draw_character(draw, ox, oy, p):
    # Colors
    FUR, FACE, EYE, SCARF, TIGER, WOOD = (139, 69, 19), (255, 222, 173), (255, 191, 0), (200, 0, 0), (255, 140, 0), (101, 67, 33)
    hx, hy = ox + 32, oy + 28 + p['hy']
    # Tail & Legs
    draw.arc([ox+10, oy+35, ox+30, oy+55], 0, 180, fill=FUR, width=3)
    for i, l_off in enumerate([p['ly'], p['ry']]):
        lx = ox + 24 + i * 12
        draw.ellipse([lx, oy+50+l_off, lx+6, oy+60+l_off], fill=FUR)
    # Body & Loincloth
    draw.ellipse([ox+20, oy+35, ox+44, oy+55], fill=FUR)
    draw.polygon([(ox+20, oy+48), (ox+44, oy+48), (ox+40, oy+56), (ox+24, oy+56)], fill=TIGER)
    # Head & Ears
    for ex in [-16, 10]: draw.ellipse([hx+ex, hy-5, hx+ex+8, hy+5], fill=FUR)
    draw.ellipse([hx-18, hy-18, hx+18, hy+16], fill=FUR)
    draw.ellipse([hx-14, hy-10, hx+14, hy+14], fill=FACE)
    # Eyes & Scarf
    for ex in [-8, 4]:
        draw.ellipse([hx+ex, hy, hx+ex+5, hy+5*p['e']], fill=EYE)
    draw.polygon([(hx-15, hy+12), (hx+15, hy+12), (hx+20, hy+22), (hx-20, hy+22)], fill=SCARF)
    draw.polygon([(hx-10, hy+22), (hx-18, hy+35), (hx-5, hy+25)], fill=SCARF)
    # Staff & Arms
    sa = math.radians(p['sa'])
    sx, sy = hx + 15 + p['sx'], hy + 15 + p['sy']
    ex, ey = sx + 25 * math.cos(sa), sy + 25 * math.sin(sa)
    draw.line([sx - 5 * math.cos(sa), sy - 5 * math.sin(sa), ex, ey], fill=WOOD, width=3)
    draw.ellipse([sx-3, sy-3, sx+5, sy+5], fill=FUR)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()

    canvas = Image.new('RGBA', (256, 192), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    for row in range(3):
        for col in range(4):
            t = col * (math.pi / 2)
            p = {'hy': 0, 'ly': 0, 'ry': 0, 'sa': -45, 'sx': 0, 'sy': 0, 'e': 1}
            
            if row == 0: # Idle
                p['hy'] = math.sin(t) * 2
                p['e'] = 0.1 if col == 3 else 1
            elif row == 1: # Walk
                p['hy'] = abs(math.sin(t)) * 2
                p['ly'] = math.sin(t * 2) * 4
                p['ry'] = -math.sin(t * 2) * 4
            elif row == 2: # Attack
                if col == 1: p.update({'sa': -80, 'sx': -5, 'sy': -5})
                if col == 2: p.update({'sa': 20, 'sx': 10, 'sy': 5, 'hy': 2})
                if col == 3: p.update({'sa': 0, 'sx': 5, 'sy': 2})
            
            draw_character(draw, col * 64, row * 64, p)

    canvas.save(args.output)

if __name__ == "__main__":
    main()