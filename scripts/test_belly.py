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

print("--- Testing Routes with 0R jumper under-belly ---")

# 1. Right motor signals to R_JMP1..3 (P1 at y=87.81)
try_add("Net-(U_PI4-GPIO12_PWMB_R)", [
    P('U_PI4', 32), (89.22, 104.00), (130.00, 104.00), (130.00, 87.81)
], width=1.0, d=1.0)

# Under belly of R_JMP1..3:
# R_JMP1 is at x=130.0, R_JMP2 is at x=133.5, R_JMP3 is at x=137.0
# P1 is at y=87.81, P2 is at y=80.19.
# At y=84.00, there is NO copper on B.Cu between y=80.19 and y=87.81!
# Let's test a track at y=84.00 from x=124.78 to x=148.81:
try_add("/I2C_SDA", [
    P('U_PI4', 3), (124.78, 84.00), (148.81, 84.00), P('J_OLED', 4)
], width=1.0, d=1.0)
