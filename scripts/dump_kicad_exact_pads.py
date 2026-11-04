import re
import json

with open('drc_test_pads.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

# Pattern for unrouted pads in DRC report:
# @(127.3200 mm, 93.5600 mm): PTH pad 1 [/+3V3_LOGIC] of U_PI4
pads = {}
for m in re.finditer(r'@\(([-\d.]+)\s+mm,\s+([-\d.]+)\s+mm\):\s+(?:PTH|SMD)?\s*pad\s+(\w+)\s+\[([^\]]+)\]\s+of\s+(\w+)', text):
    x, y, pnum, net, ref = float(m.group(1)), float(m.group(2)), m.group(3), m.group(4), m.group(5)
    if ref not in pads:
        pads[ref] = {}
    pads[ref][pnum] = {
        'x': x,
        'y': y,
        'net': net
    }

print(f"Parsed {len(pads)} footprints from DRC report.")
for ref, pdict in sorted(pads.items()):
    print(f"{ref:8s}: {len(pdict)} pads")

with open('scripts/kicad_exact_pads.json', 'w', encoding='utf-8') as f:
    json.dump(pads, f, indent=2)
print("Saved scripts/kicad_exact_pads.json")
