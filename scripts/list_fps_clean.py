import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Match each footprint block
fp_blocks = list(re.finditer(r'\(footprint\s+"([^"]+)"\s+\(layer\s+"([^"]+)"\)\s+\(uuid\s+"([^"]+)"\)\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', text))

print(f"Total footprints: {len(fp_blocks)}")
for m in fp_blocks:
    name, layer, uuid, x, y, rot = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)
    # Find reference inside the next 1000 characters
    sub = text[m.start():m.start()+1500]
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', sub)
    ref = ref_m.group(1) if ref_m else "?"
    print(f"Footprint {ref:12s} ({name:35s}) at ({x}, {y}) rot={rot or '0'}")
