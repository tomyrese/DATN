import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

# find MOTOR1, MOTOR2, MOTOR3, MOTOR4 symbols in sch
for m in ['MOTOR1', 'MOTOR2', 'MOTOR3', 'MOTOR4', 'U_TB1', 'U_TB2']:
    print(f"\n--- Symbol {m} in schematic ---")
    pos = 0
    while True:
        idx = sch.find(f'"{m}"', pos)
        if idx == -1:
            break
        # find enclosing (symbol ...)
        start = sch.rfind('(symbol', 0, idx)
        end = sch.find('\n  )', idx)
        sym_block = sch[start:end+4]
        # find pins
        pins = re.findall(r'\(pin\s+"([^"]+)"\s+\(uuid\s+"([^"]+)"\)\)', sym_block)
        print(f"Symbol found around {idx}, pins: {pins}")
        pos = idx + len(m) + 2
        if pos > len(sch): break

