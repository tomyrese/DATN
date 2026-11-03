with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
labels = re.findall(r'\(label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text)
labels.sort(key=lambda item: (float(item[1]), float(item[2])))
for n, x, y in labels:
    print(f"X={float(x):6.2f}, Y={float(y):6.2f}: {n}")
