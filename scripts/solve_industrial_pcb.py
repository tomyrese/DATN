import math
import json
import re
import uuid

from geometry_validator import test_track, all_pads
from interactive_router import chamfer_path, P, N, fps

def run_solver():
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
        
        # Test every segment
        for s in segs:
            ok, reason = test_track(s, accepted_tracks, all_pads, min_clearance=0.50)
            if not ok:
                print(f"[UNROUTED / RATSNEST] {net_name}: {reason}")
                return False
                
        # Accept
        for s in segs:
            accepted_tracks.append(s)
        print(f"[ACCEPTED] {net_name}: {len(segs)} segments (width {width}mm)")
        return True

    print("=================================================================")
    print("SOLVING INDUSTRIAL SINGLE-LAYER PCB ROUTING (0 VIAS, ZERO DRC ERRORS)")
    print("=================================================================")

    # -------------------------------------------------------------------------
    # 1. BATTERY, SWITCH, FUSE (1.4mm Power)
    # -------------------------------------------------------------------------
    try_route("/BAT+", [P('BT1', 1), P('SW1', 1)], width=1.4, is_raw=True)
    try_route("/FUSE_IN", [P('SW1', 2), (52.54, 62.00), (46.00, 68.54), P('F1', 1)], width=1.4, is_raw=True)

    # -------------------------------------------------------------------------
    # 2. MOTOR OUTPUTS (1.4mm Power) - 100% Planar, direct to screw terminals
    # -------------------------------------------------------------------------
    # Left Motors:
    try_route("/M1_A", [P('U_TB1', 12), (66.73, 52.00), (65.46, 50.73), P('J_M1', 1)], width=1.4, is_raw=True)
    try_route("/M1_B", [P('U_TB1', 13), (69.27, 52.00), (70.54, 50.73), P('J_M1', 2)], width=1.4, is_raw=True)
    try_route("/M2_B", [P('U_TB1', 14), (71.81, 55.00), (74.46, 52.35), P('J_M2', 1)], width=1.4, is_raw=True)
    try_route("/M2_A", [P('U_TB1', 15), (74.35, 57.00), (79.54, 51.81), P('J_M2', 2)], width=1.4, is_raw=True)

    # Right Motors:
    try_route("/M3_A", [P('U_TB2', 12), (138.73, 52.00), (137.46, 50.73), P('J_M3', 1)], width=1.4, is_raw=True)
    try_route("/M3_B", [P('U_TB2', 13), (141.27, 52.00), (142.54, 50.73), P('J_M3', 2)], width=1.4, is_raw=True)
    try_route("/M4_B", [P('U_TB2', 14), (143.81, 55.00), (146.46, 52.35), P('J_M4', 1)], width=1.4, is_raw=True)
    try_route("/M4_A", [P('U_TB2', 15), (146.35, 57.00), (151.54, 51.81), P('J_M4', 2)], width=1.4, is_raw=True)

    # -------------------------------------------------------------------------
    # 3. TB6612 INTERNAL U-LOOPS (1.0mm Signal) - Concentric nested loops in belly
    # -------------------------------------------------------------------------
    # TB1 Left:
    try_route("/AIN1_L", [P('U_TB1', 3), (64.19, 71.00), (69.27, 71.00), P('U_TB1', 5)], width=1.0, is_raw=True)
    try_route("/AIN2_L", [P('U_TB1', 2), (61.65, 68.00), (71.81, 68.00), P('U_TB1', 6)], width=1.0, is_raw=True)
    try_route("/PWMA_L", [P('U_TB1', 1), (59.11, 65.00), (74.35, 65.00), P('U_TB1', 7)], width=1.0, is_raw=True)

    # TB2 Right:
    try_route("/AIN1_R", [P('U_TB2', 3), (136.19, 71.00), (141.27, 71.00), P('U_TB2', 5)], width=1.0, is_raw=True)
    try_route("/AIN2_R", [P('U_TB2', 2), (133.65, 68.00), (143.81, 68.00), P('U_TB2', 6)], width=1.0, is_raw=True)
    try_route("/PWMA_R", [P('U_TB2', 1), (131.11, 65.00), (146.35, 65.00), P('U_TB2', 7)], width=1.0, is_raw=True)

    # -------------------------------------------------------------------------
    # 4. LEFT MOTOR CONTROL FROM PI 4 (1.0mm Signal) - Concentric nested tracks
    # -------------------------------------------------------------------------
    # Pin 33 (PWMA_L) turns lowest (y=90.0) to TB1.7
    # Pin 35 (AIN2_L) turns middle (y=87.5) to TB1.6
    # Pin 37 (AIN1_L) turns highest (y=85.0) to TB1.5
    try_route("/PWMA_L", [P('U_PI4', 33), (86.68, 90.00), (74.35, 90.00), P('U_TB1', 7)], width=1.0, d=1.0)
    try_route("/AIN2_L", [P('U_PI4', 35), (84.14, 87.50), (71.81, 87.50), P('U_TB1', 6)], width=1.0, d=1.0)
    try_route("/AIN1_L", [P('U_PI4', 37), (81.60, 85.00), (69.27, 85.00), P('U_TB1', 5)], width=1.0, d=1.0)

    # -------------------------------------------------------------------------
    # 5. RIGHT MOTOR CONTROL VIA JUMPERS R_JMP1..3 (1.0mm Signal)
    # -------------------------------------------------------------------------
    # South channel routes under Pi 4 to Jumpers P1 (y=87.81):
    try_route("Net-(U_PI4-GPIO12_PWMB_R)", [
        P('U_PI4', 32), (89.22, 104.00), (131.00, 104.00), (131.00, 93.00), (130.00, 92.00), P('R_JMP1', 1)
    ], width=1.0, d=1.0)
    try_route("Net-(U_PI4-GPIO16_AIN1_R)", [
        P('U_PI4', 36), (84.14, 105.50), (133.50, 105.50), P('R_JMP2', 1)
    ], width=1.0, d=1.0)
    try_route("Net-(U_PI4-GPIO20_AIN2_R)", [
        P('U_PI4', 38), (81.60, 107.00), (137.00, 107.00), P('R_JMP3', 1)
    ], width=1.0, d=1.0)

    # Jumpers P2 (y=80.19) to TB2:
    try_route("/PWMA_R", [P('R_JMP1', 2), (130.00, 77.00), (131.11, 75.89), P('U_TB2', 1)], width=1.0, is_raw=True)
    try_route("/AIN1_R", [P('R_JMP2', 2), (133.50, 75.62), P('U_TB2', 3)], width=1.0, is_raw=True)
    try_route("/AIN2_R", [P('R_JMP3', 2), (137.00, 78.50), (133.65, 78.50), P('U_TB2', 2)], width=1.0, d=0.8)

    # -------------------------------------------------------------------------
    # 6. ULTRASONIC DIVIDERS (1.0mm Signal)
    # -------------------------------------------------------------------------
    # Left US:
    try_route("Net-(U_US1-ECHO)", [P('U_US1', 3), (93.27, 51.00), (88.19, 51.00), P('R1', 1)], width=1.0, is_raw=True)
    try_route("/ECHO_L", [P('R1', 2), (95.81, 62.00), (88.19, 62.00), P('R2', 1)], width=1.0, is_raw=True)
    # Right US:
    try_route("Net-(U_US2-ECHO)", [P('U_US2', 3), (121.27, 51.00), (116.19, 51.00), P('R3', 1)], width=1.0, is_raw=True)
    try_route("/ECHO_R", [P('R3', 2), (123.81, 62.00), (116.19, 62.00), P('R4', 1)], width=1.0, is_raw=True)

    # -------------------------------------------------------------------------
    # 7. PRIMARY POWER & GROUND (1.4mm Power)
    # -------------------------------------------------------------------------
    # VM_MOTOR from F1.2 to Buck U1.1
    try_route("/VM_MOTOR", [P('F1', 2), (54.00, 76.00), (52.00, 78.00), (42.38, 78.00), P('U1', 1)], width=1.4, is_raw=True)
    # VM_MOTOR from F1.2 to TB1.9
    try_route("/VM_MOTOR", [P('F1', 2), (54.00, 62.50), (56.12, 60.38), P('U_TB1', 9)], width=1.4, is_raw=True)
    # VM_MOTOR along North Channel (y=38.5) to C2.1 and TB2.9
    try_route("/VM_MOTOR", [
        (42.38, 78.00), (40.00, 78.00), (40.00, 38.50), (133.00, 38.50), P('C2', 1)
    ], width=1.4, d=1.0)
    try_route("/VM_MOTOR", [P('C2', 1), (133.00, 48.00), (131.11, 49.89), P('U_TB2', 9)], width=1.4, is_raw=True)

    # Ground Star:
    # U1.2 (GND IN-) to BT1.2
    try_route("/GND", [P('U1', 2), (47.46, 82.00), (44.00, 82.00), (44.00, 42.00), P('BT1', 2)], width=1.4, d=1.0)
    # TB1 GND pins: 11 to 16, 16 to 8
    try_route("/GND", [P('U_TB1', 11), P('U_TB1', 16)], width=1.4, is_raw=True)
    try_route("/GND", [P('U_TB1', 16), (76.89, 68.00), P('U_TB1', 8)], width=1.4, is_raw=True)
    # TB2 GND pins: 11 to 16, 16 to 8
    try_route("/GND", [P('U_TB2', 11), P('U_TB2', 16)], width=1.4, is_raw=True)
    try_route("/GND", [P('U_TB2', 16), (148.89, 68.00), P('U_TB2', 8)], width=1.4, is_raw=True)

    # C3 and C4 Power / Ground to Pi 4:
    try_route("/+5V_PWR", [P('U_PI4', 2), P('U_PI4', 4)], width=1.4, is_raw=True)
    try_route("/+5V_PWR", [P('U_PI4', 4), P('C3', 1)], width=1.4, is_raw=True)
    try_route("/+5V_PWR", [P('C3', 1), P('C4', 1)], width=1.4, is_raw=True)
    try_route("/GND", [P('U_PI4', 6), (122.24, 98.00), (124.00, 98.00), P('C4', 2)], width=1.4, is_raw=True)
    try_route("/GND", [P('C4', 2), P('C3', 2)], width=1.4, is_raw=True)

    # +3V3_LOGIC from Pi4 Pin 1 to OLED Pin 1:
    try_route("/+3V3_LOGIC", [P('U_PI4', 1), (127.32, 91.50), (141.19, 91.50), P('J_OLED', 1)], width=1.0, d=1.0)

    print("=================================================================")
    print(f"SOLVER FINISHED: {len(accepted_tracks)} total track segments accepted.")
    print("=================================================================")
    return accepted_tracks

if __name__ == '__main__':
    run_solver()
