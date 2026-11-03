import re
from PIL import Image, ImageDraw, ImageFont

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Zoomed in region around J_OLED: X in [130, 160], Y in [36, 65]
scale = 50 # 50 pixels per mm for extreme high definition!
ox, oy = 130.0, 36.0
img_w = int((162.0 - ox) * scale)
img_h = int((65.0 - oy) * scale)

img = Image.new('RGB', (img_w, img_h), (252, 252, 253))
draw = ImageDraw.Draw(img)

def p2i(x, y):
    return (int((x - ox) * scale), int((y - oy) * scale))

# Draw board outline
lines = re.findall(r'\(gr_line\s+\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\).*?\(layer\s+"Edge\.Cuts"\)', text, re.DOTALL)
for x1, y1, x2, y2 in lines:
    draw.line([p2i(float(x1), float(y1)), p2i(float(x2), float(y2))], fill=(180, 20, 20), width=6)

# Draw segments
segments = re.findall(r'\(segment\s+\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(width\s+([0-9\.\-]+)\).*?\(net\s+"([^"]*)"\)', text, re.DOTALL)
for x1, y1, x2, y2, w, net in segments:
    color = (0, 90, 200)
    if 'GND' in net: color = (40, 40, 40)
    elif '5V' in net or 'VM' in net: color = (210, 40, 40)
    elif '3V3' in net: color = (230, 140, 0)
    width_px = max(2, int(float(w) * scale))
    draw.line([p2i(float(x1), float(y1)), p2i(float(x2), float(y2))], fill=color, width=width_px)

# Draw footprints & pads in this area
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
    
    px, py = p2i(base_x, base_y)
    if ref == 'J_OLED':
        draw.rectangle([px-20, py-20, px+20, py+20], fill=(160, 32, 240, 60), outline=(140, 0, 200), width=3)
        draw.text((px-50, py-45), f"★ J_OLED (1.3\" I2C Header)", fill=(120, 0, 180))
    else:
        draw.rectangle([px-10, py-10, px+10, py+10], fill=(0, 160, 60, 60), outline=(0, 100, 30), width=2)
        draw.text((px+15, py-15), ref, fill=(0, 100, 30))

    # Silk rect
    for sr in re.finditer(r'\(fp_rect\s+\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)', fp_str):
        rx1, ry1, rx2, ry2 = float(sr.group(1)), float(sr.group(2)), float(sr.group(3)), float(sr.group(4))
        sp1 = p2i(base_x + rx1, base_y + ry1)
        sp2 = p2i(base_x + rx2, base_y + ry2)
        draw.rectangle([sp1, sp2], outline=(100, 100, 100), width=2)

    # Footprint pads
    for p in re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+([0-9\.\-]+)\s+([0-9\.\-]+)\).*?\(net\s+"([^"]*)"\)', fp_str, re.DOTALL):
        num, px, py, sx, sy, net = p.group(1), float(p.group(2)), float(p.group(3)), float(p.group(4)), float(p.group(5)), p.group(6)
        rx = px * math.cos(rad) - py * math.sin(rad)
        ry = px * math.sin(rad) + py * math.cos(rad)
        ax, ay = base_x + rx, base_y + ry
        cpx, cpy = p2i(ax, ay)
        pr = max(4, int(float(sx) * scale / 2))
        pad_fill = (255, 120, 255) if ref == 'J_OLED' else (255, 215, 0)
        draw.ellipse([cpx - pr, cpy - pr, cpx + pr, cpy + pr], fill=pad_fill, outline=(150, 100, 0), width=2)
        # Pad label text
        pin_names = {"1": "1: VCC (+3.3V)", "2": "2: GND", "3": "3: SCL (GPIO1)", "4": "4: SDA (GPIO0)"}
        lbl = pin_names.get(num, f"Pin {num}")
        draw.text((cpx - 25, cpy + pr + 5), lbl, fill=(0, 0, 0))

out_png = 'extracted_imgs/pcb_oled_zoom.png'
img.save(out_png)
print(f"Saved {out_png}")

import shutil
shutil.copyfile(out_png, r'C:\Users\Wuys\.gemini\antigravity\brain\ab345fbe-c8ae-4a31-b829-16c1f5b13c06\pcb_oled_zoom.png')
print("Copied zoom to artifacts dir.")

