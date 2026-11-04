import json
import math
from geometry_validator import test_track, all_pads
from interactive_router import chamfer_path

with open('scripts/kicad_exact_pads.json', 'r', encoding='utf-8') as f:
    k_pads = json.load(f)

# Reload all_pads
all_pads.clear()
for ref, pdict in k_pads.items():
    for pnum, p in pdict.items():
        all_pads.append({
            'ref': ref,
            'pnum': pnum,
            'x': p['x'],
            'y': p['y'],
            'net_id': 1,
            'net_name': p['net'],
            'radius': 1.0 # 2.0mm pad size
        })

print(f"Loaded {len(all_pads)} exact pads.")

def P(ref, pnum):
    p = k_pads[ref][str(pnum)]
    return (p['x'], p['y'])

accepted_tracks = []

def try_route(net_name, pts, width=1.0, d=1.2, is_raw=False):
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
            print(f"[REJECT / RATSNEST] {net_name}: {reason} | seg {s['p1']} -> {s['p2']}")
            return False
            
    for s in segs:
        accepted_tracks.append(s)
    print(f"[ACCEPTED] {net_name}: {len(segs)} segs")
    return True

print("\n--- 1. Power Supply ---")
try_route("/BAT+", [P('BT1', 1), P('SW1', 1)], width=1.4, is_raw=True)
try_route("/FUSE_IN", [P('SW1', 2), (52.54, 62.00), (46.00, 68.54), P('F1', 1)], width=1.4, is_raw=True)
try_route("/VM_MOTOR", [P('F1', 2), (54.00, 76.00), (52.00, 78.00), (42.38, 78.00), P('U1', 1)], width=1.4, is_raw=True)
try_route("/VM_MOTOR", [P('U_TB1', 9), (56.00, 60.38), (56.00, 49.75), P('C1', 1)], width=1.4, d=0.8)

print("\n--- 2. Motor Outputs Left & Right (1.4mm) ---")
try_route("/M1_A", [P('U_TB1', 12), (66.73, 52.00), (65.46, 50.73), P('J_M1', 1)], width=1.4, is_raw=True)
try_route("/M1_B", [P('U_TB1', 13), (69.27, 52.00), (70.54, 50.73), P('J_M1', 2)], width=1.4, is_raw=True)
try_route("/M2_B", [P('U_TB1', 14), (71.81, 55.00), (74.46, 52.35), P('J_M2', 1)], width=1.4, is_raw=True)
try_route("/M2_A", [P('U_TB1', 15), (74.35, 57.00), (79.54, 51.81), P('J_M2', 2)], width=1.4, is_raw=True)

try_route("/M3_A", [P('U_TB2', 12), (138.73, 52.00), (137.46, 50.73), P('J_M3', 1)], width=1.4, is_raw=True)
try_route("/M3_B", [P('U_TB2', 13), (141.27, 52.00), (142.54, 50.73), P('J_M3', 2)], width=1.4, is_raw=True)
try_route("/M4_B", [P('U_TB2', 14), (143.81, 55.00), (146.46, 52.35), P('J_M4', 1)], width=1.4, is_raw=True)
try_route("/M4_A", [P('U_TB2', 15), (146.35, 57.00), (151.54, 51.81), P('J_M4', 2)], width=1.4, is_raw=True)

print("\n--- 3. TB6612 Internal U-Loops (1.0mm) ---")
try_route("/AIN1_L", [P('U_TB1', 3), (64.19, 71.00), (69.27, 71.00), P('U_TB1', 5)], width=1.0, is_raw=True)
try_route("/AIN2_L", [P('U_TB1', 2), (61.65, 68.00), (71.81, 68.00), P('U_TB1', 6)], width=1.0, is_raw=True)
try_route("/PWMA_L", [P('U_TB1', 1), (59.11, 65.00), (74.35, 65.00), P('U_TB1', 7)], width=1.0, is_raw=True)

try_route("/AIN1_R", [P('U_TB2', 3), (136.19, 71.00), (141.27, 71.00), P('U_TB2', 5)], width=1.0, is_raw=True)
try_route("/AIN2_R", [P('U_TB2', 2), (133.65, 68.00), (143.81, 68.00), P('U_TB2', 6)], width=1.0, is_raw=True)
try_route("/PWMA_R", [P('U_TB2', 1), (131.11, 65.00), (146.35, 65.00), P('U_TB2', 7)], width=1.0, is_raw=True)

print("\n--- 4. Left Motor Control from Pi 4 (1.0mm) ---")
try_route("/AIN1_L", [P('U_PI4', 37), (81.60, 90.00), (69.27, 90.00), P('U_TB1', 5)], width=1.0, d=1.0)
try_route("/AIN2_L", [P('U_PI4', 35), (84.14, 87.50), (71.81, 87.50), P('U_TB1', 6)], width=1.0, d=1.0)
try_route("/PWMA_L", [P('U_PI4', 33), (86.68, 85.00), (74.35, 85.00), P('U_TB1', 7)], width=1.0, d=1.0)

print("\n--- 5. Right Motor Control via Jumpers R_JMP1..3 (1.0mm) ---")
try_route("Net-(U_PI4-GPIO12_PWMB_R)", [
    P('U_PI4', 32), (89.22, 104.00), (131.00, 104.00), (131.00, 93.00), (130.00, 92.00), P('R_JMP1', 1)
], width=1.0, d=1.0)
try_route("Net-(U_PI4-GPIO16_AIN1_R)", [
    P('U_PI4', 36), (84.14, 105.50), (133.50, 105.50), P('R_JMP2', 1)
], width=1.0, d=1.0)
try_route("Net-(U_PI4-GPIO20_AIN2_R)", [
    P('U_PI4', 38), (81.60, 107.00), (137.00, 107.00), P('R_JMP3', 1)
], width=1.0, d=1.0)

try_route("/PWMA_R", [P('R_JMP1', 2), (130.00, 77.00), (131.11, 75.89), P('U_TB2', 1)], width=1.0, is_raw=True)

print("\n--- 6. Ultrasonic Sensor Dividers (1.0mm) ---")
try_route("Net-(U_US1-ECHO)", [P('U_US1', 3), (93.27, 51.00), (88.19, 51.00), P('R1', 1)], width=1.0, is_raw=True)
try_route("/ECHO_L", [P('R1', 2), (95.81, 62.00), (88.19, 62.00), P('R2', 1)], width=1.0, is_raw=True)
try_route("Net-(U_US2-ECHO)", [P('U_US2', 3), (121.27, 51.00), (116.19, 51.00), P('R3', 1)], width=1.0, is_raw=True)
try_route("/ECHO_R", [P('R3', 2), (123.81, 62.00), (116.19, 62.00), P('R4', 1)], width=1.0, is_raw=True)

print("\n--- 7. Pi 4 +5V_PWR ---")
try_route("/+5V_PWR", [P('U_PI4', 2), P('U_PI4', 4)], width=1.4, is_raw=True)

print(f"\nTotal accepted tracks: {len(accepted_tracks)} segments.")
