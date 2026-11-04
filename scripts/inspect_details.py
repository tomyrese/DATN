import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find footprints
fp_matches = list(re.finditer(r'\(footprint\s+"([^"]+)"[\s\S]*?\n\s*\)', text))

print(f"Total footprints found: {len(fp_matches)}")

for m in fp_matches:
    fp_text = m.group(0)
    ref_m = re.search(r'\(fp_text reference "([^"]+)"', fp_text)
    val_m = re.search(r'\(fp_text value "([^"]+)"', fp_text)
    at_m = re.search(r'\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)', fp_text)
    ref = ref_m.group(1) if ref_m else "?"
    val = val_m.group(1) if val_m else "?"
    at = at_m.groups() if at_m else ("?", "?", "?")
    print(f"\nFootprint {ref} ({val}) at {at}:")
    
    # Extract pads
    pads = re.findall(r'\(pad\s+"([^"]+)"\s+(\w+)\s+(\w+)\s+\(at\s+([-\d\.]+)\s+([-\d\.]+)(?:\s+([-\d\.]+))?\)(?:[\s\S]*?\(net\s+(\d+)\s+"([^"]+)"\))?', fp_text)
    for p in pads:
        p_num, p_type, p_shape, px, py, prot, net_num, net_name = p
        print(f"  Pad {p_num:>3}: at ({float(px):>7.3f}, {float(py):>7.3f}) rot={prot or '0':>4} | Net: {net_name or 'unconnected'}")

