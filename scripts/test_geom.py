import math
import os
import re

def parse_footprint_pads(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    pads = {}
    matches = re.finditer(r'\(pad\s+"([^"]+)"\s+(?:thru_hole|smd)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', text)
    for m in matches:
        p_num = m.group(1)
        lx = float(m.group(2))
        ly = float(m.group(3))
        lrot = float(m.group(4)) if m.group(4) else 0.0
        pads[p_num] = (lx, ly, lrot)
    return pads

def get_world_pad(x0, y0, rot_deg, lx, ly):
    rad = math.radians(rot_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    wx = x0 + lx * cos_a - ly * sin_a
    wy = y0 + lx * sin_a + ly * cos_a
    return round(wx, 4), round(wy, 4)

tb_pads = parse_footprint_pads('libraries/robot_electronics.pretty/Module_TB6612FNG_Breakout.kicad_mod')
print(f"TB6612 Breakout local pads count: {len(tb_pads)}")
for p in ['1', '8', '9', '16']:
    lx, ly, _ = tb_pads[p]
    w90 = get_world_pad(67.69, 68.8275, 90, lx, ly)
    w270 = get_world_pad(67.69, 68.8275, 270, lx, ly)
    print(f"Pad {p:2}: local=({lx:6.2f}, {ly:6.2f}) -> rot90=({w90[0]:6.2f}, {w90[1]:6.2f}) | rot270=({w270[0]:6.2f}, {w270[1]:6.2f})")

