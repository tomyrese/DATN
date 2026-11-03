import re, math, os, shutil
from PIL import Image, ImageDraw, ImageFont

with open('robot_electronics.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Zoom into Pi4 & OLED: X in [95, 156], Y in [78, 106]
scale = 50
ox, oy = 95.0, 78.0
img_w = int((156.0 - ox) * scale)
img_h = int((106.0 - oy) * scale)

img = Image.new('RGB', (img_w, img_h), (250, 252, 255))
draw = ImageDraw.Draw(img)

# Fonts
font_path = 'C:/Windows/Fonts/segoeuib.ttf' if os.path.exists('C:/Windows/Fonts/segoeuib.ttf') else 'C:/Windows/Fonts/segoeui.ttf'
font_title = ImageFont.truetype(font_path, 22)
font_label = ImageFont.truetype(font_path, 16)
font_small = ImageFont.truetype(font_path, 13)

def p2i(x, y):
    return (int((x - ox) * scale), int((y - oy) * scale))

def draw_dashed_line(draw_obj, p1, p2, fill, width=4, dash_len=14, gap_len=8):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    if dist == 0: return
    ux = dx / dist
    uy = dy / dist
    curr = 0
    while curr < dist:
        end = min(curr + dash_len, dist)
        sp = (int(p1[0] + ux * curr), int(p1[1] + uy * curr))
        ep = (int(p1[0] + ux * end), int(p1[1] + uy * end))
        draw_obj.line([sp, ep], fill=fill, width=width)
        curr += dash_len + gap_len

# Draw B.Cu segments
segments = re.findall(r'\(segment\s+\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(width\s+([0-9\.\-]+)\)\s+\(layer\s+"([^"]*)"\)\s+\(net\s+"([^"]*)"\)', text, re.DOTALL)
for x1, y1, x2, y2, w, layer, net in segments:
    x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
    if not (ox-5 <= x1 <= 156+5 and oy-5 <= y1 <= 106+5 or ox-5 <= x2 <= 156+5 and oy-5 <= y2 <= 106+5):
        continue
    width_px = max(2, int(float(w) * scale))
    if layer == "B.Cu":
        color = (40, 120, 220)
        if 'GND' in net: color = (80, 80, 90)
        elif '5V' in net: color = (220, 40, 40)
        elif '3V3' in net: color = (235, 140, 0)
        elif 'SCL' in net: color = (10, 150, 190)
        elif 'SDA' in net: color = (180, 50, 200)
        draw.line([p2i(x1, y1), p2i(x2, y2)], fill=color, width=width_px)

# Draw F.SilkS guide lines (Jumper lines)
for m in re.finditer(r'\(gr_line\b', text):
    start = m.start()
    depth = 0
    end = start
    while end < len(text):
        if text[end] == '(': depth += 1
        elif text[end] == ')':
            depth -= 1
            if depth == 0:
                end += 1
                break
        end += 1
    block = text[start:end]
    if '"F.SilkS"' in block:
        m_pts = re.search(r'\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)', block)
        if m_pts:
            x1, y1, x2, y2 = map(float, m_pts.groups())
            if ox-5 <= x1 <= 156+5 and oy-5 <= y1 <= 106+5 or ox-5 <= x2 <= 156+5 and oy-5 <= y2 <= 106+5:
                draw_dashed_line(draw, p2i(x1, y1), p2i(x2, y2), fill=(0, 180, 60), width=4, dash_len=14, gap_len=8)

# Draw vias (Jumper pads & feedthroughs)
vias = re.findall(r'\(via\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+([0-9\.\-]+)\)', text, re.DOTALL)
for vx, vy, vs in vias:
    vx, vy = float(vx), float(vy)
    if ox <= vx <= 156 and oy <= vy <= 106:
        cpx, cpy = p2i(vx, vy)
        r = int(float(vs) * scale / 2)
        draw.ellipse([cpx - r, cpy - r, cpx + r, cpy + r], fill=(255, 215, 0), outline=(140, 100, 0), width=2)
        draw.ellipse([cpx - 3, cpy - 3, cpx + 3, cpy + 3], fill=(30, 30, 30))

# Draw footprints & pads
for m in re.finditer(r'\(footprint\s+"([^"]+)".*?\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)(?:\s+([0-9\.\-]+))?\).*?\(property\s+"Reference"\s+"([^"]+)"', text, re.DOTALL):
    base_x, base_y = float(m.group(2)), float(m.group(3))
    rot_val = float(m.group(4)) if m.group(4) else 0.0
    ref = m.group(5)
    start_fp = m.start()
    end_fp = text.find('(footprint', start_fp + 10)
    if end_fp == -1: end_fp = text.find('(embedded_fonts', start_fp)
    fp_str = text[start_fp:end_fp]
    rad = math.radians(rot_val)

    if ref in ['J_OLED', 'Rasp_PI4', 'RIGHT']:
        px, py = p2i(base_x, base_y)
        if ref == 'J_OLED':
            draw.text((px-90, py-50), "★ J_OLED (1.3\" I2C 128x64)", fill=(140, 0, 180), font=font_title)
        elif ref == 'Rasp_PI4':
            draw.text((px-70, py-35), "Raspberry Pi 4 (40-Pin Header)", fill=(0, 120, 50), font=font_label)

        for p in re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+([0-9\.\-]+)\s+([0-9\.\-]+)\).*?\(net\s+"([^"]*)"\)', fp_str, re.DOTALL):
            pnum, px_rel, py_rel = p.group(1), float(p.group(2)), float(p.group(3))
            pnet = p.group(6)
            rx = px_rel * math.cos(rad) - py_rel * math.sin(rad)
            ry = px_rel * math.sin(rad) + py_rel * math.cos(rad)
            ax, ay = base_x + rx, base_y + ry
            if ox <= ax <= 156 and oy <= ay <= 106:
                cpx, cpy = p2i(ax, ay)
                pr = max(4, int(0.7 * scale))
                pfill = (255, 120, 255) if ref == 'J_OLED' else (255, 230, 80)
                draw.ellipse([cpx - pr, cpy - pr, cpx + pr, cpy + pr], fill=pfill, outline=(150, 100, 0), width=2)
                if ref == 'J_OLED':
                    pnames = {'1': '3V3', '2': 'GND', '3': 'SCL', '4': 'SDA'}
                    label = f"P{pnum}:{pnames.get(pnum, '')}"
                    draw.text((cpx - 18, cpy + 14), label, fill=(120, 0, 160), font=font_label)
                elif pnum in ['17', '27', '28', '6', '4', '1', '2', '39']:
                    draw.text((cpx - 12, cpy - 24), f"P{pnum}", fill=(0, 100, 30), font=font_small)

# Draw F.SilkS texts
for m in re.finditer(r'\(gr_text\b', text):
    start = m.start()
    depth = 0
    end = start
    while end < len(text):
        if text[end] == '(': depth += 1
        elif text[end] == ')':
            depth -= 1
            if depth == 0:
                end += 1
                break
        end += 1
    block = text[start:end]
    if '"F.SilkS"' in block:
        m_txt = re.search(r'\(gr_text\s+"([^"]+)"\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)', block)
        if m_txt:
            stext, sx, sy = m_txt.group(1), float(m_txt.group(2)), float(m_txt.group(3))
            if ox <= sx <= 156 and oy <= sy <= 106:
                tx, ty = p2i(sx, sy)
                if 'JMP' in stext:
                    draw.text((tx - 45, ty - 22), f"➔ {stext}", fill=(0, 140, 50), font=font_label)
                else:
                    draw.text((tx - 25, ty - 10), stext, fill=(40, 40, 40), font=font_small)

out_png = 'extracted_imgs/pcb_zoom_completed.png'
os.makedirs('extracted_imgs', exist_ok=True)
img.save(out_png)
print(f"Saved {out_png}")

art_dir = r"C:\Users\Wuys\.gemini\antigravity\brain\ab345fbe-c8ae-4a31-b829-16c1f5b13c06"
if os.path.exists(art_dir):
    shutil.copy(out_png, os.path.join(art_dir, "pcb_zoom_completed.png"))
    print("Copied zoom to artifact dir.")
