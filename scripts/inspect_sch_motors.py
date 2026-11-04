import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

symbols = text.split('(symbol ')
for s in symbols:
    if 'MOTOR1' in s or 'MOTOR2' in s or 'MOTOR3' in s or 'MOTOR4' in s:
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', s)
        val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', s)
        at_m = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)', s)
        ref = ref_m.group(1) if ref_m else '?'
        val = val_m.group(1) if val_m else '?'
        at = (at_m.group(1), at_m.group(2)) if at_m else '?'
        print(f"Symbol {ref} ({val}) at {at}")
        # find pin connections
        pins = re.findall(r'\(pin\s+"([^"]+)"\s+\(uuid\s+"([^"]+)"\)\)', s)
        print("  Pins:", pins)

