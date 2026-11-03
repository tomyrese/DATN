import re, math, os, shutil
from PIL import Image, ImageDraw, ImageFont

with open('robot_electronics.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

scale = 25
ox, oy = 45.0, 35.0
img_w = int((165.0 - ox) * scale)
img_h = int((115.0 - oy) * scale)

img = Image.new('RGB', (img_w, img_h), (250, 252, 255))
draw = ImageDraw.Draw(img)

# Fonts
font_path = 'C:/Windows/Fonts/segoeuib.ttf' if os.path.exists('C:/Windows/Fonts/segoeuib.ttf') else 'C:/Windows/Fonts/segoeui.ttf'
font_title = ImageFont.truetype(font_path, 18)
font_label = ImageFont.truetype(font_path, 14)
font_small = ImageFont.truetype(font_path, 12)

def p2i(x, y):
    return (int((x - ox) * scale), int((y - oy) * scale))

def draw_dashed_line(draw_obj, p1, p2, fill, width=4, dash_len=12, gap_len=6):
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

# Draw board outline (Edge.Cuts)
lines = re.findall(r'\(gr_line\s+\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\).*?\(layer\s+"Edge\.Cuts"\)', text, re.DOTALL)
for x1, y1, x2, y2 in lines:
    draw.line([p2i(float(x1), float(y1)), p2i(float(x2), float(y2))], fill=(180, 30, 30), width=4)

# Draw B.Cu segments (copper tracks)
segments = re.findall(r'\(segment\s+\(start\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(end\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(width\s+([0-9\.\-]+)\)\s+\(layer\s+"([^"]*)"\)\s+\(net\s+"([^"]*)"\)', text, re.DOTALL)
for x1, y1, x2, y2, w, layer, net in segments:
    if layer == "B.Cu":
        color = (30, 110, 210) # B.Cu signal blue
        if 'GND' in net: color = (60, 60, 70) # GND dark slate
        elif '5V' in net or 'VM' in net: color = (210, 35, 35) # Power red
        elif '3V3' in net: color = (235, 130, 0) # 3V3 orange
        width_px = max(2, int(float(w) * scale))
        draw.line([p2i(float(x1), float(y1)), p2i(float(x2), float(y2))], fill=color, width=width_px)

# Parse & draw F.SilkS guide lines (Top Wire Jumpers)
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
            draw_dashed_line(draw, p2i(x1, y1), p2i(x2, y2), fill=(0, 160, 60), width=4, dash_len=12, gap_len=6)

# Draw vias (Jumper connection pads & power feedthroughs)
vias = re.findall(r'\(via\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+([0-9\.\-]+)\)', text, re.DOTALL)
for vx, vy, vs in vias:
    cpx, cpy = p2i(float(vx), float(vy))
    r = int(float(vs) * scale / 2)
    draw.ellipse([cpx - r, cpy - r, cpx + r, cpy + r], fill=(255, 215, 0), outline=(130, 90, 0), width=2)
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
    px, py = p2i(base_x, base_y)
    
    if ref == 'J_OLED':
        draw.rectangle([px-14, py-14, px+14, py+14], fill=(180, 40, 220), outline=(120, 0, 160), width=3)
        draw.text((px-40, py-36), "★ J_OLED (1.3\" I2C)", fill=(130, 0, 180), font=font_label)
    elif 'MOTOR' in ref:
        draw.rectangle([px-8, py-8, px+8, py+8], fill=(0, 150, 180), outline=(0, 90, 120))
        draw.text((px+10, py-8), ref, fill=(0, 90, 120), font=font_small)
    else:
        draw.rectangle([px-6, py-6, px+6, py+6], fill=(0, 140, 50), outline=(0, 90, 30))
        draw.text((px+8, py-8), ref, fill=(0, 90, 30), font=font_small)

    # Pads
    for p in re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)\s+\(size\s+([0-9\.\-]+)\s+([0-9\.\-]+)\)', fp_str):
        num, px_rel, py_rel, sx, sy = p.group(1), float(p.group(2)), float(p.group(3)), float(p.group(4)), float(p.group(5))
        rx = px_rel * math.cos(rad) - py_rel * math.sin(rad)
        ry = px_rel * math.sin(rad) + py_rel * math.cos(rad)
        ax, ay = base_x + rx, base_y + ry
        cpx, cpy = p2i(ax, ay)
        pr = max(2, int(float(sx) * scale / 2))
        pad_fill = (255, 120, 255) if ref == 'J_OLED' else (255, 220, 50)
        draw.ellipse([cpx - pr, cpy - pr, cpx + pr, cpy + pr], fill=pad_fill, outline=(160, 100, 0), width=1)

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
            tx, ty = p2i(sx, sy)
            if 'JMP' in stext:
                draw.text((tx - 40, ty - 18), f"➔ {stext}", fill=(0, 130, 40), font=font_label)
            elif 'SINGLE-SIDED' in stext:
                draw.text((tx - 180, ty - 10), stext, fill=(180, 20, 20), font=font_title)
            else:
                draw.text((tx - 20, ty - 8), stext, fill=(40, 40, 40), font=font_small)

# Add Legend
draw.rectangle([20, 20, 450, 155], fill=(255, 255, 255), outline=(150, 150, 150), width=2)
draw.text((30, 25), "CHÚ THÍCH THIẾT KẾ PCB 1 LỚP (SINGLE-SIDED):", fill=(0, 0, 0), font=font_title)
draw.line([(30, 58), (60, 58)], fill=(30, 110, 210), width=4)
draw.text((70, 48), "B.Cu: Đường tín hiệu (Signal Track 1.0mm)", fill=(0, 0, 0), font=font_label)
draw_dashed_line(draw, (30, 82), (60, 82), fill=(0, 160, 60), width=4, dash_len=6, gap_len=4)
draw.text((70, 72), "F.SilkS: Cầu cắm dây mặt trên (Jumpers JMP1..5)", fill=(0, 130, 40), font=font_label)
draw.line([(30, 106), (60, 106)], fill=(60, 60, 70), width=5)
draw.text((70, 96), "B.Cu: Đường Mass (GND Track 1.4mm)", fill=(0, 0, 0), font=font_label)
draw.line([(30, 130), (60, 130)], fill=(210, 35, 35), width=5)
draw.text((70, 120), "B.Cu: Đường Nguồn (5V/VM Track 1.4-1.5mm)", fill=(0, 0, 0), font=font_label)

out_png = 'extracted_imgs/pcb_complete_routed.png'
os.makedirs('extracted_imgs', exist_ok=True)
img.save(out_png)
print(f"Saved {out_png}")

art_dir = r"C:\Users\Wuys\.gemini\antigravity\brain\ab345fbe-c8ae-4a31-b829-16c1f5b13c06"
if os.path.exists(art_dir):
    shutil.copy(out_png, os.path.join(art_dir, "pcb_complete_routed.png"))
    print("Copied to artifact dir.")
