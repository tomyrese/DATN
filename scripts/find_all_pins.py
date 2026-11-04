with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+\d+\)\s+\(length\s+[\d\.\-]+\)\s+\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', text)
for p in pins:
    print(f"Pin {p[3]:2s} ({p[2]:20s}) at rel ({float(p[0]):6.2f}, {float(p[1]):6.2f}) -> world ({float(p[0])+105.41:6.2f}, {180.34-float(p[1]):6.2f})")

