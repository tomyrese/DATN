with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
left_fp = re.search(r'\(footprint\s+"Module_TB6612FNG_Breakout"[\s\S]*?\(property\s+"Reference"\s+"LEFT"[\s\S]*?\n\t\)', text)
if left_fp:
    # Print pads of left
    pads = re.findall(r'\(pad\s+"(\d+)"[\s\S]*?\(net\s+"([^"]*)"\)', left_fp.group(0))
    for p in pads:
        print(f"Pad {p[0]:>2}: net={p[1]}")
