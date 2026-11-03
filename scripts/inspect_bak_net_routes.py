with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    bak = f.read()

import re
segments = re.findall(r'\(segment[\s\S]*?\n\t\)', bak)

def print_net(name):
    print(f"=== Segments for {name} ===")
    for s in segments:
        if f'(net "{name}")' in s:
            start_m = re.search(r'\(start\s+([-\d\.]+)\s+([-\d\.]+)', s)
            end_m = re.search(r'\(end\s+([-\d\.]+)\s+([-\d\.]+)', s)
            w_m = re.search(r'\(width\s+([-\d\.]+)', s)
            print(f"  ({float(start_m.group(1)):.2f}, {float(start_m.group(2)):.2f}) -> ({float(end_m.group(1)):.2f}, {float(end_m.group(2)):.2f}) w={w_m.group(1)}")

print_net("/PWMA_L")
print_net("/M1_A")
print_net("/M2_A")
