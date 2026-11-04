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
    
    # Test all segments of this track
    for s in segs:
        ok, reason = test_track(s, accepted_tracks, all_pads, min_clearance=0.50)
        if not ok:
            print(f"REJECT {net_name}: {reason} | seg {s['p1']} -> {s['p2']}")
            return False
            
    # All segments valid, add them
    for s in segs:
        accepted_tracks.append(s)
    print(f"ACCEPT {net_name}: {len(segs)} segments")
    return True

print("--- Testing Routes ---")

# 1. BAT+
try_add("/BAT+", [P('BT1', 1), P('SW1', 1)], width=1.4, is_raw=True)

# 2. FUSE_IN
try_add("/FUSE_IN", [P('SW1', 2), (52.54, 62.00), (46.00, 68.54), P('F1', 1)], width=1.4, is_raw=True)

# 3. Motor Outputs Left
try_add("/M1_A", [P('U_TB1', 12), (66.73, 52.00), (65.46, 50.73), P('J_M1', 1)], width=1.4, is_raw=True)
try_add("/M1_B", [P('U_TB1', 13), (69.27, 52.00), (70.54, 50.73), P('J_M1', 2)], width=1.4, is_raw=True)
try_add("/M2_B", [P('U_TB1', 14), (71.81, 55.00), (74.46, 52.35), P('J_M2', 1)], width=1.4, is_raw=True)
try_add("/M2_A", [P('U_TB1', 15), (74.35, 57.00), (79.54, 51.81), P('J_M2', 2)], width=1.4, is_raw=True)

# 4. Motor Outputs Right
try_add("/M3_A", [P('U_TB2', 12), (138.73, 52.00), (137.46, 50.73), P('J_M3', 1)], width=1.4, is_raw=True)
try_add("/M3_B", [P('U_TB2', 13), (141.27, 52.00), (142.54, 50.73), P('J_M3', 2)], width=1.4, is_raw=True)
try_add("/M4_B", [P('U_TB2', 14), (143.81, 55.00), (146.46, 52.35), P('J_M4', 1)], width=1.4, is_raw=True)
try_add("/M4_A", [P('U_TB2', 15), (146.35, 57.00), (151.54, 51.81), P('J_M4', 2)], width=1.4, is_raw=True)

# 5. U_TB1 Internal U-Loops
# Note: distance between rows 1-8 (y=75.62) and 9-16 (y=60.38) is 15.24mm!
# y values: 71.0, 68.0, 65.0
try_add("/AIN1_L", [P('U_TB1', 3), (64.19, 71.00), (69.27, 71.00), P('U_TB1', 5)], width=1.0, is_raw=True)
try_add("/AIN2_L", [P('U_TB1', 2), (61.65, 68.00), (71.81, 68.00), P('U_TB1', 6)], width=1.0, is_raw=True)
try_add("/PWMA_L", [P('U_TB1', 1), (59.11, 65.00), (74.35, 65.00), P('U_TB1', 7)], width=1.0, is_raw=True)

# 6. U_TB2 Internal U-Loops
try_add("/AIN1_R", [P('U_TB2', 3), (136.19, 71.00), (141.27, 71.00), P('U_TB2', 5)], width=1.0, is_raw=True)
try_add("/AIN2_R", [P('U_TB2', 2), (133.65, 68.00), (143.81, 68.00), P('U_TB2', 6)], width=1.0, is_raw=True)
try_add("/PWMA_R", [P('U_TB2', 1), (131.11, 65.00), (146.35, 65.00), P('U_TB2', 7)], width=1.0, is_raw=True)

# 7. Left Motor Control from Pi 4
# U_PI4: Pin 37=(81.60, 93.56) [/AIN1_L], Pin 35=(84.14, 93.56) [/AIN2_L], Pin 33=(86.68, 93.56) [/PWMA_L]
# Connecting to U_TB1 pins 5=(69.27, 75.62), 6=(71.81, 75.62), 7=(74.35, 75.62)
# Since Pin 37 is left-most, it goes to Pin 5 (left-most)!
# Pin 35 (middle) goes to Pin 6 (middle)!
# Pin 33 (right-most) goes to Pin 7 (right-most)!
# Perfect planar match!
try_add("/AIN1_L", [P('U_PI4', 37), (81.60, 83.00), (69.27, 83.00), P('U_TB1', 5)], width=1.0, d=1.0)
try_add("/AIN2_L", [P('U_PI4', 35), (84.14, 85.50), (71.81, 85.50), P('U_TB1', 6)], width=1.0, d=1.0)
try_add("/PWMA_L", [P('U_PI4', 33), (86.68, 88.00), (74.35, 88.00), P('U_TB1', 7)], width=1.0, d=1.0)

# 8. Right Motor Control from Pi 4 to Jumpers R_JMP1, R_JMP2, R_JMP3
# Even pins: Pin 32=(89.22, 96.10), Pin 36=(84.14, 96.10), Pin 38=(81.60, 96.10)
# Jumpers P1: R_JMP1.1=(130.00, 87.81), R_JMP2.1=(133.50, 87.81), R_JMP3.1=(137.00, 87.81)
try_add("Net-(U_PI4-GPIO12_PWMB_R)", [P('U_PI4', 32), (89.22, 104.00), (130.00, 104.00), P('R_JMP1', 1)], width=1.0, d=1.0)
try_add("Net-(U_PI4-GPIO16_AIN1_R)", [P('U_PI4', 36), (84.14, 105.50), (133.50, 105.50), P('R_JMP2', 1)], width=1.0, d=1.0)
try_add("Net-(U_PI4-GPIO20_AIN2_R)", [P('U_PI4', 38), (81.60, 107.00), (137.00, 107.00), P('R_JMP3', 1)], width=1.0, d=1.0)

# Jumpers P2 to U_TB2
try_add("/PWMA_R", [P('R_JMP1', 2), (130.00, 77.00), (131.11, 75.89), P('U_TB2', 1)], width=1.0, is_raw=True)
try_add("/AIN1_R", [P('R_JMP2', 2), (133.50, 78.00), (136.19, 78.00), P('U_TB2', 3)], width=1.0, d=0.8)
try_add("/AIN2_R", [P('R_JMP3', 2), (137.00, 79.50), (133.65, 79.50), P('U_TB2', 2)], width=1.0, d=0.8)

# 9. Ultrasonic Dividers
# Left US
try_add("Net-(U_US1-ECHO)", [P('U_US1', 3), (93.27, 51.00), (88.19, 51.00), P('R1', 1)], width=1.0, is_raw=True)
try_add("/ECHO_L", [P('R1', 2), (95.81, 62.00), (88.19, 62.00), P('R2', 1)], width=1.0, is_raw=True)
# Right US
try_add("Net-(U_US2-ECHO)", [P('U_US2', 3), (121.27, 51.00), (116.19, 51.00), P('R3', 1)], width=1.0, is_raw=True)
try_add("/ECHO_R", [P('R3', 2), (123.81, 62.00), (116.19, 62.00), P('R4', 1)], width=1.0, is_raw=True)

# 10. OLED
# U_PI4.3=(124.78, 93.56), J_OLED.4=(147.54, 95.00)
# U_PI4.5=(122.24, 93.56), J_OLED.3=(142.46, 95.00)
try_add("/I2C_SDA", [P('U_PI4', 3), (124.78, 90.00), (147.54, 90.00), P('J_OLED', 4)], width=1.0, d=1.0)
try_add("/I2C_SCL", [P('U_PI4', 5), (122.24, 88.50), (142.46, 88.50), P('J_OLED', 3)], width=1.0, d=1.0)

print(f"\nTotal accepted tracks: {len(accepted_tracks)} segments")
