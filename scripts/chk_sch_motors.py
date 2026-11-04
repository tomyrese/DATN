import re

with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    sch = f.read()

labels = re.findall(r'\((?:label|global_label|hierarchical_label)\s+"([^"]+)"', sch)
motor_labels = [l for l in set(labels) if any(m in l for m in ['M1', 'M2', 'M3', 'M4'])]
print("Motor labels in schematic:", sorted(motor_labels))

