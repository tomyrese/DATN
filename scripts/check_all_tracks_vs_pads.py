import json, math

with open('scripts/world_pads.json', 'r') as f:
    comps = json.load(f)

# Collect all pads
pads = []
for comp, pad_dict in comps.items():
    for p_num, pos in pad_dict.items():
        pads.append({
            'comp': comp,
            'pin': p_num,
            'x': pos['x'],
            'y': pos['y']
        })

import sys
sys.path.append('scripts')
from solve_planar_pcb_v16 import paths

def dist_point_to_seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

print("=== CHECKING TRACK TO PAD CLEARANCES ===")
tight = []
for p in pads:
    for seg in paths:
        d = dist_point_to_seg(p['x'], p['y'], seg['p1'][0], seg['p1'][1], seg['p2'][0], seg['p2'][1])
        # If distance < 1.8mm (meaning gap between pad radius 1.0mm and track radius 0.5mm is < 0.3mm)
        # And neither endpoint is this pad
        d_p1 = math.hypot(p['x'] - seg['p1'][0], p['y'] - seg['p1'][1])
        d_p2 = math.hypot(p['x'] - seg['p2'][0], p['y'] - seg['p2'][1])
        if d_p1 > 0.05 and d_p2 > 0.05:
            # Clearance from pad edge (radius 1.0) to track edge (radius seg['width']/2)
            clearance = d - 1.0 - (seg['width'] / 2.0)
            if clearance < 0.50:
                tight.append((clearance, d, p, seg))

print(f"Total tight clearances (< 0.50mm): {len(tight)}")
# Sort by clearance
tight.sort(key=lambda x: x[0])
for cl, d, p, seg in tight[:20]:
    print(f"Clearance {cl*1000:5.1f} um (dist={d:.2f}mm): Pad {p['comp']} Pin {p['pin']} at ({p['x']}, {p['y']}) to seg {seg['net']} ({seg['p1']}->{seg['p2']})")

