with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find where U_PI4 is defined
idx = text.find('"U_PI4"')
if idx != -1:
    start = text.rfind('(symbol', 0, idx)
    end = text.find('\n  )', idx)
    print("Found U_PI4 symbol block:")
    print(text[start:start+2500])

