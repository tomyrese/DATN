with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Find the symbol definition for Raspberry_Pi_4_40Pin in the schematic header
m = re.search(r'\(symbol\s+"robot_electronics:Raspberry_Pi_4_40Pin"[\s\S]*?\n\t\t\)', text)
if m:
    print(m.group(0)[:1500])
else:
    # search for pin name and numbers
    pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+\d+\)\s+\(length\s+[\d\.\-]+\)\s+\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', text)
    print(f"Found {len(pins)} pin definitions")
    for p in pins[:40]:
        print(f"Pin {p[3]:2s} ({p[2]:20s}) at rel ({p[0]}, {p[1]})")

