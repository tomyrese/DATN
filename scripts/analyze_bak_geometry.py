import math
import re

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb.bak', 'r', encoding='utf-8') as f:
    text = f.read()

# Check corners in .bak
segments = []
for m in re.finditer(r'\(segment\s+\(start\s+([-\d.]+)\s+([-\d.]+)\)\s+\(end\s+([-\d.]+)\s+([-\d.]+)\)\s+\(width\s+([-\d.]+)\)\s+\(layer\s+"([^"]+)"\)\s+\(net\s+(?:\d+\s+)?"([^"]+)"\)', text):
    p1 = (float(m.group(1)), float(m.group(2)))
    p2 = (float(m.group(3)), float(m.group(4)))
    w = float(m.group(5))
    layer = m.group(6)
    net = m.group(7)
    segments.append({'p1': p1, 'p2': p2, 'w': w, 'layer': layer, 'net': net})

print(f"Total segments in .bak: {len(segments)}")

# Check 90 degree corners
corners_90 = 0
for i in range(len(segments)):
    for j in range(i + 1, len(segments)):
        if segments[i]['net'] != segments[j]['net']: continue
        s1, s2 = segments[i], segments[j]
        # check shared endpoint
        shared = None
        if math.hypot(s1['p1'][0]-s2['p1'][0], s1['p1'][1]-s2['p1'][1]) < 0.01:
            v1 = (s1['p2'][0]-s1['p1'][0], s1['p2'][1]-s1['p1'][1])
            v2 = (s2['p2'][0]-s2['p1'][0], s2['p2'][1]-s2['p1'][1])
        elif math.hypot(s1['p1'][0]-s2['p2'][0], s1['p1'][1]-s2['p2'][1]) < 0.01:
            v1 = (s1['p2'][0]-s1['p1'][0], s1['p2'][1]-s1['p1'][1])
            v2 = (s2['p1'][0]-s2['p2'][0], s2['p1'][1]-s2['p2'][1])
        elif math.hypot(s1['p2'][0]-s2['p1'][0], s1['p2'][1]-s2['p1'][1]) < 0.01:
            v1 = (s1['p1'][0]-s1['p2'][0], s1['p1'][1]-s1['p2'][1])
            v2 = (s2['p2'][0]-s2['p1'][0], s2['p2'][1]-s2['p1'][1])
        elif math.hypot(s1['p2'][0]-s2['p2'][0], s1['p2'][1]-s2['p2'][1]) < 0.01:
            v1 = (s1['p1'][0]-s1['p2'][0], s1['p1'][1]-s1['p2'][1])
            v2 = (s2['p1'][0]-s2['p2'][0], s2['p1'][1]-s2['p2'][1])
        else:
            continue
        
        len1 = math.hypot(v1[0], v1[1])
        len2 = math.hypot(v2[0], v2[1])
        if len1 > 0.01 and len2 > 0.01:
            dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (len1 * len2)
            if abs(dot) < 0.15: # ~90 deg
                corners_90 += 1

print(f"Total ~90 degree corners in .bak: {corners_90}")

