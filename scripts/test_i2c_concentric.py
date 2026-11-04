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

print("--- Testing Concentric I2C ---")

# SCL is inner: Pi4.5 (122.24) -> OLED.3 (146.27) at y=85.0
try_add("/I2C_SCL", [
    P('U_PI4', 5), (122.24, 85.00), (146.27, 85.00), P('J_OLED', 3)
], width=1.0, d=1.0)

# SDA is outer: Pi4.3 (124.78) -> OLED.4 (148.81) at y=83.0
try_add("/I2C_SDA", [
    P('U_PI4', 3), (124.78, 83.00), (148.81, 83.00), P('J_OLED', 4)
], width=1.0, d=1.0)
