import json, re, math

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

from test_fp_swap import swap_tb6612_rows, mirror_pi4_header

def parse_fp_pads(fp_text):
    m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', fp_text)
    fp_x = float(m_at.group(1))
    fp_y = float(m_at.group(2))
    fp_rot = float(m_at.group(3)) if m_at.group(3) else 0.0

    pads = {}
    for pm in re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)[\s\S]*?\(net\s+"([^"]*)"\)', fp_text):
        num = pm.group(1)
        px = float(pm.group(2))
        py = float(pm.group(3))
        rad = math.radians(fp_rot)
        wx = fp_x + px * math.cos(rad) - py * math.sin(rad)
        wy = fp_y + px * math.sin(rad) + py * math.cos(rad)
        pads[num] = {'x': round(wx, 4), 'y': round(wy, 4), 'net': pm.group(5)}
    return pads

first_seg = text.find('(segment')
base = text[:first_seg]

fps = {}
for m in re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\n\t\)', base):
    fp_str = m.group(0)
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_str)
    ref = ref_m.group(1) if ref_m else "UNKNOWN"
    if ref in ['LEFT', 'RIGHT']:
        fp_str = swap_tb6612_rows(fp_str)
    elif ref == 'Rasp_PI4':
        fp_str = mirror_pi4_header(fp_str)
    fps[ref] = parse_fp_pads(fp_str)

with open('scripts/world_pads_v2.json', 'w', encoding='utf-8') as f:
    json.dump(fps, f, indent=2)

print("World pads v2 saved successfully.")
for k, v in fps.items():
    print(f"{k:12s}: {len(v)} pads. Pad 1: {v.get('1')}")
