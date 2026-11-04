import math
import os
import re
import uuid

from zero_conflict_base import (
    world_pads, components, net_names, net_id, get_net_id,
    pad, chamfer_path
)
from geometry_checker import check_clearance, point_to_seg_dist, seg_distance

# Proposed track candidate generator
def generate_candidates():
    candidates = []

    def add(net, pts, width=1.0, d=1.2):
        c_pts = chamfer_path(pts, d=d)
        nid = get_net_id(net)
        canonical = net if net.startswith('/') or net.startswith('Net-') else '/' + net
        for i in range(len(c_pts) - 1):
            candidates.append({
                'net': canonical,
                'net_id': nid,
                'p1': c_pts[i],
                'p2': c_pts[i+1],
                'width': width
            })

    def raw(net, pts, width=1.0):
        nid = get_net_id(net)
        canonical = net if net.startswith('/') or net.startswith('Net-') else '/' + net
        for i in range(len(pts) - 1):
            candidates.append({
                'net': canonical,
                'net_id': nid,
                'p1': pts[i],
                'p2': pts[i+1],
                'width': width
            })

    # Priority 1: Battery, Switch, Fuse, Buck Power
    raw("/BAT+", [pad('BT1', 1), pad('SW1', 1)], width=1.4)
    add("/FUSE_IN", [pad('SW1', 2), (52.54, 63.00), (46.00, 63.00), pad('F1', 1)], width=1.4)

    # Priority 2: VM_MOTOR
    add("/VM_MOTOR", [pad('F1', 2), (54.00, 78.00), (42.38, 78.00), pad('U1', 1)], width=1.4)
    add("/VM_MOTOR", [pad('F1', 2), (54.00, 60.38), pad('U_TB1', 9)], width=1.4)
    add("/VM_MOTOR", [pad('U_TB1', 9), (59.11, 48.00), pad('C1', 1)], width=1.4)
    add("/VM_MOTOR", [pad('C1', 1), (43.00, 48.00), (43.00, 38.50), (133.00, 38.50), pad('C2', 1)], width=1.4)
    add("/VM_MOTOR", [pad('C2', 1), (133.00, 60.38), pad('U_TB2', 9)], width=1.4)

    # Priority 3: Motor Outputs
    raw("/M1_A", [pad('U_TB1', 12), pad('J_M1', 1)], width=1.4)
    raw("/M1_B", [pad('U_TB1', 13), pad('J_M1', 2)], width=1.4)
    add("/M2_B", [pad('U_TB1', 14), (71.81, 55.00), (74.46, 55.00), pad('J_M2', 1)], width=1.4)
    add("/M2_A", [pad('U_TB1', 15), (74.35, 57.00), (79.54, 57.00), pad('J_M2', 2)], width=1.4)

    raw("/M3_A", [pad('U_TB2', 12), pad('J_M3', 1)], width=1.4)
    raw("/M3_B", [pad('U_TB2', 13), pad('J_M3', 2)], width=1.4)
    add("/M4_B", [pad('U_TB2', 14), (143.81, 55.00), (146.46, 55.00), pad('J_M4', 1)], width=1.4)
    add("/M4_A", [pad('U_TB2', 15), (146.35, 57.00), (151.54, 57.00), pad('J_M4', 2)], width=1.4)

    # Priority 4: Left Motor Control
    add("/AIN1_L", [pad('U_TB1', 3), (64.19, 72.50), (69.27, 72.50), pad('U_TB1', 5)], width=1.0)
    add("/AIN2_L", [pad('U_TB1', 2), (61.65, 69.50), (71.81, 69.50), pad('U_TB1', 6)], width=1.0)
    add("/PWMA_L", [pad('U_TB1', 1), (59.11, 66.50), (74.35, 66.50), pad('U_TB1', 7)], width=1.0)

    add("/AIN1_L", [pad('U_PI4', 37), (81.60, 83.00), (69.27, 83.00), pad('U_TB1', 5)], width=1.0)
    add("/AIN2_L", [pad('U_PI4', 35), (84.14, 85.50), (71.81, 85.50), pad('U_TB1', 6)], width=1.0)
    add("/PWMA_L", [pad('U_PI4', 33), (86.68, 88.00), (74.35, 88.00), pad('U_TB1', 7)], width=1.0)

    # Priority 5: Right Motor Control
    add("/AIN1_R", [pad('U_TB2', 3), (136.19, 72.50), (141.27, 72.50), pad('U_TB2', 5)], width=1.0)
    add("/AIN2_R", [pad('U_TB2', 2), (133.65, 69.50), (143.81, 69.50), pad('U_TB2', 6)], width=1.0)
    add("/PWMA_R", [pad('U_TB2', 1), (131.11, 66.50), (146.35, 66.50), pad('U_TB2', 7)], width=1.0)

    add("Net-(U_PI4-GPIO12_PWMB_R)", [pad('U_PI4', 32), (89.22, 105.00), (129.50, 105.00), pad('R_JMP1', 1)], width=1.0)
    add("Net-(U_PI4-GPIO16_AIN1_R)", [pad('U_PI4', 36), (84.14, 106.50), (133.50, 106.50), pad('R_JMP2', 1)], width=1.0)
    add("Net-(U_PI4-GPIO20_AIN2_R)", [pad('U_PI4', 38), (81.60, 108.00), (137.50, 108.00), pad('R_JMP3', 1)], width=1.0)

    raw("/PWMA_R", [pad('R_JMP1', 2), pad('U_TB2', 1)], width=1.0)
    add("/AIN1_R", [pad('R_JMP2', 2), (133.50, 77.00), (136.19, 77.00), pad('U_TB2', 3)], width=1.0)
    add("/AIN2_R", [pad('R_JMP3', 2), (137.50, 78.50), (133.65, 78.50), pad('U_TB2', 2)], width=1.0)

    # Priority 6: Line Sensor
    add("/LINE_R", [pad('U_PI4', 23), (99.38, 55.00), (103.46, 55.00), pad('U_LINE', 2)], width=1.0)
    add("/LINE_C", [pad('U_PI4', 21), (101.92, 57.00), (106.00, 57.00), pad('U_LINE', 3)], width=1.0)
    add("/LINE_L", [pad('U_PI4', 19), (104.46, 59.00), (108.54, 59.00), pad('U_LINE', 4)], width=1.0)

    # Priority 7: Ultrasonic Dividers
    raw("Net-(U_US1-ECHO)", [pad('U_US1', 3), (93.27, 52.00), (88.19, 52.00), pad('R1', 1)], width=1.0)
    raw("/ECHO_L", [pad('R1', 2), (95.81, 62.00), (88.19, 62.00), pad('R2', 1)], width=1.0)
    raw("Net-(U_US2-ECHO)", [pad('U_US2', 3), (121.27, 52.00), (116.19, 52.00), pad('R3', 1)], width=1.0)
    raw("/ECHO_R", [pad('R3', 2), (123.81, 62.00), (116.19, 62.00), pad('R4', 1)], width=1.0)

    # Priority 8: Primary Power & Ground
    add("/GND", [pad('U1', 2), (47.00, 88.00), (47.00, 42.00), pad('BT1', 2)], width=1.4)
    add("/GND", [pad('BT1', 2), (53.00, 42.00), pad('C1', 2)], width=1.4)
    add("/GND", [pad('C1', 2), (53.00, 63.00), (64.19, 63.00), pad('U_TB1', 11)], width=1.4)
    raw("/GND", [pad('U_TB1', 11), pad('U_TB1', 16)], width=1.4)
    raw("/GND", [pad('U_TB1', 16), pad('U_TB1', 8)], width=1.4)

    add("/GND", [pad('U1', 4), (58.00, 93.56), pad('U_PI4', 39)], width=1.4)
    raw("/GND", [pad('U_PI4', 39), pad('U_PI4', 34)], width=1.4)
    raw("/GND", [pad('U_PI4', 34), pad('U_PI4', 30)], width=1.4)
    raw("/GND", [pad('U_PI4', 30), pad('U_PI4', 25)], width=1.4)
    raw("/GND", [pad('U_PI4', 25), pad('U_PI4', 20)], width=1.4)
    raw("/GND", [pad('U_PI4', 20), pad('U_PI4', 14)], width=1.4)
    raw("/GND", [pad('U_PI4', 14), pad('U_PI4', 9)], width=1.4)
    raw("/GND", [pad('U_PI4', 9), pad('U_PI4', 6)], width=1.4)

    return candidates

# Filter candidates to ensure ZERO DRC violations
def filter_zero_violations(candidates):
    accepted = []
    rejected_count = 0

    for cand in candidates:
        temp_list = accepted + [cand]
        v = check_clearance(temp_list, world_pads, min_clearance=0.5)
        if len(v) == 0:
            accepted.append(cand)
        else:
            rejected_count += 1
            # print(f"Rejected segment {cand['net']}: {v[0]}")

    print(f"Candidates: {len(candidates)}, Accepted: {len(accepted)}, Rejected (ratsnest): {rejected_count}")
    return accepted

accepted_tracks = filter_zero_violations(generate_candidates())
v_final = check_clearance(accepted_tracks, world_pads, min_clearance=0.5)
print(f"Final Clearance Violations: {len(v_final)}")
