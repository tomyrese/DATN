with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re, math

for m in re.finditer(r'\(footprint\s+"Module_TB6612FNG_Breakout"[\s\S]*?\n\t\)', text):
    fp = m.group(0)
    if 'LEFT' in fp:
        m_at = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)', fp)
        cx, cy, rot = float(m_at.group(1)), float(m_at.group(2)), float(m_at.group(3))
        print(f"LEFT footprint center: ({cx}, {cy}), rot: {rot}")

        for p in re.finditer(r'\(pad\s+"([0-9]+)"[\s\S]*?\(at\s+([-\d\.]+)\s+([-\d\.]+)', fp):
            num = p.group(1)
            lx, ly = float(p.group(2)), float(p.group(3))
            rad = math.radians(rot)
            wx = cx + lx * math.cos(rad) - ly * math.sin(rad)
            wy = cy + lx * math.sin(rad) + ly * math.cos(rad)
            print(f"Pad {num:2s}: local ({lx:6.2f}, {ly:6.2f}) -> world ({wx:6.2f}, {wy:6.2f})")
        break
