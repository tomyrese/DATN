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

print("--- Testing Power / Cap Routes ---")

# Pi 4 Pin 2 to Pin 4 (+5V_PWR)
try_add("/+5V_PWR", [P('U_PI4', 2), P('U_PI4', 4)], width=1.4, is_raw=True)

# Pi 4 Pin 4 to C3.1
try_add("/+5V_PWR", [P('U_PI4', 4), (124.78, 98.00), (126.00, 99.22), P('C3', 1)], width=1.4, is_raw=True)

# Pi 4 Pin 6 to C3.2 (GND) via south jog
# C3.2 is at (128.5, 100.0)
try_add("/GND", [P('U_PI4', 6), (122.24, 101.50), (128.50, 101.50), P('C3', 2)], width=1.4, d=0.8)
