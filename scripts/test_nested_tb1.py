import math
import json
from geometry_validator import test_track, all_pads
from interactive_router import chamfer_path, P, N, fps

accepted_tracks = []

def try_add(net_name, pts, width=1.0, d=1.2, is_raw=False):
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

print("--- Testing Nested Pi4 to TB1 ---")

# AIN1_L (inner): Pi4.37 (81.60) -> TB1.5 (69.27) turning at y=90.0
try_add("/AIN1_L", [P('U_PI4', 37), (81.60, 90.00), (69.27, 90.00), P('U_TB1', 5)], width=1.0, d=1.0)

# AIN2_L (middle): Pi4.35 (84.14) -> TB1.6 (71.81) turning at y=87.5
try_add("/AIN2_L", [P('U_PI4', 35), (84.14, 87.50), (71.81, 87.50), P('U_TB1', 6)], width=1.0, d=1.0)

# PWMA_L (outer): Pi4.33 (86.68) -> TB1.7 (74.35) turning at y=85.0
try_add("/PWMA_L", [P('U_PI4', 33), (86.68, 85.00), (74.35, 85.00), P('U_TB1', 7)], width=1.0, d=1.0)
