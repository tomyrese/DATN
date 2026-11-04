import math
import json
from geometry_validator import test_track, all_pads
from interactive_router import chamfer_path, P, N, fps
from generate_clean_industrial_pcb import build_pcb

accepted_tracks = build_pcb()

def try_add_more(net_name, pts, width=1.0, d=1.2, is_raw=False):
    c_pts = pts if is_raw else chamfer_path(pts, d=d)
    segs = []
    for i in range(len(c_pts) - 1):
        segs.append({
            'net_name': net_name,
            'p1': c_pts[i],
            'p2': c_pts[i+1],
            'width': width
        })
    
    for s in segs:
        ok, reason = test_track(s, accepted_tracks, all_pads, min_clearance=0.50)
        if not ok:
            print(f"REJECT {net_name}: {reason} | seg {s['p1']} -> {s['p2']}")
            return False
            
    for s in segs:
        accepted_tracks.append(s)
    print(f"ACCEPT {net_name}: {len(segs)} segments")
    return True

print("\n--- Testing additional clean routes ---")

# 1. C1.1 to North Channel VM_MOTOR
try_add_more("/VM_MOTOR", [P('C1', 1), (53.00, 38.50)], width=1.4, is_raw=True)

# 2. TB1.9 to C1.1
try_add_more("/VM_MOTOR", [P('U_TB1', 9), (56.00, 60.38), (56.00, 46.25), P('C1', 1)], width=1.4, d=1.0)

# 3. TB2.9 to C2.1
try_add_more("/VM_MOTOR", [P('U_TB2', 9), (131.11, 48.00), (133.00, 48.00), P('C2', 1)], width=1.4, is_raw=True)

# 4. R2.2 (GND) to R4.2 (GND) ?
# R2.2 is at (95.81, 66.00), R4.2 is at (123.81, 66.00)
# Line sensor is at x=106, y=45. Pin 1 of Line is at x=100.92, y=45.
