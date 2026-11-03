import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

segs = re.findall(r'\(segment\s+\(start\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(end\s+([-\d\.]+)\s+([-\d\.]+)\)\s+\(width\s+([-\d\.]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+"?([^"\s\)]+)"?\)', text)
print(f"Total segments: {len(segs)}")
for s in segs[:15]:
    print(s)
