with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find Raspberry Pi symbol
m = re.search(r'\(symbol\s+[\s\S]*?\(property\s+"Reference"\s+"Rasp_PI4"[\s\S]*?\n\t\)', text)
if m:
    print("Found Rasp_PI4")
    # let's find pin locations or wires connected around (53.34, y) and (157.48, y)
    labels = re.findall(r'\(label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text)
    pi_labels = [(n, float(x), float(y)) for n, x, y in labels if x in ['53.34', '157.48']]
    pi_labels.sort(key=lambda item: (item[1], item[2]))
    for n, x, y in pi_labels:
        print(f"X={x:6.2f}, Y={y:6.2f}: {n}")
