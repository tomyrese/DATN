import sys, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

for pcb_name in ['Pi4_Robot_Carrier_1Layer.kicad_pcb', 'robot_electronics.kicad_pcb', 'Pi4_Robot_Carrier_Panel_4x_A4.kicad_pcb']:
    print(f"=== {pcb_name} ===")
    with open(pcb_name, 'r', encoding='utf-8') as f:
        text = f.read()

    pad_counts = Counter()
    for m in re.finditer(r'\(pad\s+"([^"]+)"\s+(\w+)\s+(\w+)(.*?)\n\s+\)', text, re.DOTALL):
        body = m.group(0)
        shape = m.group(3)
        s_m = re.search(r'\(size\s+([0-9\.]+)\s+([0-9\.]+)\)', body)
        d_m = re.search(r'\(drill\s+([0-9\.]+)\)', body)
        pad_counts[(shape, s_m.groups() if s_m else None, d_m.group(1) if d_m else None)] += 1

    for k, v in pad_counts.items():
        print("  Pad:", k, "->", v)

    via_counts = Counter()
    for m in re.finditer(r'\(via\b.*?\n\t\)', text, re.DOTALL):
        body = m.group(0)
        s_m = re.search(r'\(size\s+([0-9\.]+)\)', body)
        d_m = re.search(r'\(drill\s+([0-9\.]+)\)', body)
        via_counts[(s_m.group(1) if s_m else None, d_m.group(1) if d_m else None)] += 1

    for k, v in via_counts.items():
        print("  Via:", k, "->", v)
