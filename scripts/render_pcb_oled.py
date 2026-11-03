import re
from PIL import Image, ImageDraw, ImageFont

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Board dimensions: X=[49.0, 160.45], Y=[37.23, 110.0]
scale = 20
ox, oy = 45.0, 35.0
img_w = int((165.0 - ox) * scale)
img_h = int((115.0 - oy) * scale)

img = Image.new('RGB', (img_w, img_h), (252, 252, 253))
draw = ImageDraw.Draw(img)

def p2i(x, y):
    return (int((x - ox) * scale), int((y - oy) * scale))

# Draw board outline (Edge.Cuts)
lines = re.findall(r'\(gr_line\s+\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\).*?\(layer\s+"Edge\.Cuts"\)', text, re.DOTALL)
for x1, y1, x2, y2 in lines:
    draw.line([p2i(float(x1), float(y1)), p2i(float(x2), float(y2))], fill=(180, 20, 20), width=4)

# Draw segments (copper tracks)
segments = re.findall(r'\(segment\s+\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(width\s+([0-9\.\-]+)\).*?\(net\s+"([^"]*)"\)', text, re.DOTALL)
for x1, y1, x2, y2, w, net in segments:
    color = (0, 90, 200) # signal blue
    if 'GND' in net: color = (40, 40, 40) # GND dark gray
    elif '5V' in net or 'VM' in net: color = (210, 40, 40) # Power red
    elif '3V3' in net: color = (230, 140, 0) # 3V3 orange
    width_px = max(2, int(float(w) * scale))
    draw.line([p2i(float(x1), float(y1)), p2i(float(x2), float(y2))], fill=color, width=width_px)

# Draw vias (jumpers)
vias = re.findall(r'\(via\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+([0-9\.\-]+)\)', text, re.DOTALL)
for vx, vy, vs in vias:
    cpx, cpy = p2i(float(vx), float(vy))
    r = int(float(vs) * scale / 2)
    draw.ellipse([cpx - r, cpy - r, cpx + r, cpy + r], fill=(200, 180, 50), outline=(100, 80, 0), width=2)

# Draw footprints & pads
for m in re.finditer(r'\(footprint\s+"([^"]+)".*?\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)(?:\s+([0-9\.\-]+))?\).*?\(property\s+"Reference"\s+"([^"]+)"', text, re.DOTALL):
    base_x, base_y = float(m.group(2)), float(m.group(3))
    rot_val = float(m.group(4)) if m.group(4) else 0.0
    ref = m.group(5)
    start_fp = m.start()
    end_fp = text.find('(footprint', start_fp + 10)
    if end_fp == -1: end_fp = text.find('(embedded_fonts', start_fp)
    fp_str = text[start_fp:end_fp]
    
    import math
    rad = math.radians(rot_val)
    
    # Footprint marker
    px, py = p2i(base_x, base_y)
    if ref == 'J_OLED':
        # Highlight J_OLED in vibrant purple
        draw.rectangle([px-12, py-12, px+12, py+12], fill=(160, 32, 240), outline=(100, 0, 160), width=2)
        draw.text((px-25, py-30), f"★ {ref} (OLED 1.3\")", fill=(140, 0, 200))
    else:
        draw.rectangle([px-6, py-6, px+6, py+6], fill=(0, 160, 60), outline=(0, 100, 30))
        draw.text((px+8, py-8), ref, fill=(0, 100, 30))

    # Footprint pads
    for p in re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)', fp_str):
        num, px, py, sx, sy = p.group(1), float(p.group(2)), float(p.group(3)), float(p.group(4)), float(p.group(5))
        rx = px * math.cos(rad) - py * math.sin(rad)
        ry = px * math.sin(rad) + py * math.cos(rad)
        ax, ay = base_x + rx, base_y + ry
        cpx, cpy = p2i(ax, ay)
        pr = max(2, int(float(sx) * scale / 2))
        pad_fill = (255, 100, 255) if ref == 'J_OLED' else (255, 215, 0)
        draw.ellipse([cpx - pr, cpy - pr, cpx + pr, cpy + pr], fill=pad_fill, outline=(150, 100, 0), width=1)

# Save
out_png = 'extracted_imgs/pcb_with_oled_visual.png'
img.save(out_png)
print(f"Saved {out_png}")

# Also copy to artifacts dir
import shutil
shutil.copyfile(out_png, r'C:\Users\Wuys\.gemini\antigravity\brain\ab345fbe-c8ae-4a31-b829-16c1f5b13c06\pcb_with_oled_visual.png')
print("Copied to artifacts dir.")

