from zero_conflict_base import (
    world_pads, components, net_names, net_id, get_net_id,
    pad, add_trace, add_raw, tracks
)
from geometry_checker import check_clearance

def route_clean():
    tracks.clear()

    # 1. /BAT+
    add_raw("/BAT+", [pad('BT1', 1), pad('SW1', 1)], width=1.4)

    # 2. /FUSE_IN
    add_trace("/FUSE_IN", [pad('SW1', 2), (52.54, 63.00), (46.00, 63.00), pad('F1', 1)], width=1.4)

    # 3. /VM_MOTOR
    add_trace("/VM_MOTOR", [pad('F1', 2), (54.00, 78.00), (42.38, 78.00), pad('U1', 1)], width=1.4)
    add_trace("/VM_MOTOR", [pad('F1', 2), (54.00, 60.38), pad('U_TB1', 9)], width=1.4)
    add_trace("/VM_MOTOR", [pad('U_TB1', 9), (59.11, 48.00), pad('C1', 1)], width=1.4)
    add_trace("/VM_MOTOR", [pad('C1', 1), (43.00, 48.00), (43.00, 38.50), (133.00, 38.50), pad('C2', 1)], width=1.4)
    add_trace("/VM_MOTOR", [pad('C2', 1), (133.00, 60.38), pad('U_TB2', 9)], width=1.4)

    # 4. Motor Outputs
    add_raw("/M1_A", [pad('U_TB1', 12), pad('J_M1', 1)], width=1.4)
    add_raw("/M1_B", [pad('U_TB1', 13), pad('J_M1', 2)], width=1.4)
    add_trace("/M2_B", [pad('U_TB1', 14), (71.81, 55.00), (74.46, 55.00), pad('J_M2', 1)], width=1.4)
    add_trace("/M2_A", [pad('U_TB1', 15), (74.35, 57.00), (79.54, 57.00), pad('J_M2', 2)], width=1.4)

    add_raw("/M3_A", [pad('U_TB2', 12), pad('J_M3', 1)], width=1.4)
    add_raw("/M3_B", [pad('U_TB2', 13), pad('J_M3', 2)], width=1.4)
    add_trace("/M4_B", [pad('U_TB2', 14), (143.81, 55.00), (146.46, 55.00), pad('J_M4', 1)], width=1.4)
    add_trace("/M4_A", [pad('U_TB2', 15), (146.35, 57.00), (151.54, 57.00), pad('J_M4', 2)], width=1.4)

    # 5. Left Motor Control
    add_trace("/AIN1_L", [pad('U_TB1', 3), (64.19, 72.50), (69.27, 72.50), pad('U_TB1', 5)], width=1.0)
    add_trace("/AIN2_L", [pad('U_TB1', 2), (61.65, 69.50), (71.81, 69.50), pad('U_TB1', 6)], width=1.0)
    add_trace("/PWMA_L", [pad('U_TB1', 1), (59.11, 66.50), (74.35, 66.50), pad('U_TB1', 7)], width=1.0)

    add_trace("/AIN1_L", [pad('U_PI4', 37), (81.60, 83.00), (69.27, 83.00), pad('U_TB1', 5)], width=1.0)
    add_trace("/AIN2_L", [pad('U_PI4', 35), (84.14, 85.50), (71.81, 85.50), pad('U_TB1', 6)], width=1.0)
    add_trace("/PWMA_L", [pad('U_PI4', 33), (86.68, 88.00), (74.35, 88.00), pad('U_TB1', 7)], width=1.0)

    # 6. Right Motor Control
    add_trace("/AIN1_R", [pad('U_TB2', 3), (136.19, 72.50), (141.27, 72.50), pad('U_TB2', 5)], width=1.0)
    add_trace("/AIN2_R", [pad('U_TB2', 2), (133.65, 69.50), (143.81, 69.50), pad('U_TB2', 6)], width=1.0)
    add_trace("/PWMA_R", [pad('U_TB2', 1), (131.11, 66.50), (146.35, 66.50), pad('U_TB2', 7)], width=1.0)

    add_trace("Net-(U_PI4-GPIO12_PWMB_R)", [pad('U_PI4', 32), (89.22, 104.50), (129.50, 104.50), pad('R_JMP1', 1)], width=1.0)
    add_trace("Net-(U_PI4-GPIO16_AIN1_R)", [pad('U_PI4', 36), (84.14, 106.00), (133.50, 106.00), pad('R_JMP2', 1)], width=1.0)
    add_trace("Net-(U_PI4-GPIO20_AIN2_R)", [pad('U_PI4', 38), (81.60, 107.50), (137.50, 107.50), pad('R_JMP3', 1)], width=1.0)

    add_raw("/PWMA_R", [pad('R_JMP1', 2), pad('U_TB2', 1)], width=1.0)
    add_raw("/AIN1_R", [pad('R_JMP2', 2), (133.50, 77.00), (136.19, 77.00), pad('U_TB2', 3)], width=1.0)
    add_raw("/AIN2_R", [pad('R_JMP3', 2), (137.50, 78.50), (133.65, 78.50), pad('U_TB2', 2)], width=1.0)

    # 7. OLED
    add_trace("/I2C_SDA", [pad('U_PI4', 3), (124.78, 92.50), (148.81, 92.50), pad('J_OLED', 4)], width=1.0)
    add_trace("/I2C_SCL", [pad('U_PI4', 5), (122.24, 91.00), (146.27, 91.00), pad('J_OLED', 3)], width=1.0)
    add_trace("/+3V3_LOGIC", [pad('U_PI4', 1), (127.32, 94.00), (141.19, 94.00), pad('J_OLED', 1)], width=1.4)
    add_trace("/GND", [pad('U_PI4', 6), (122.24, 96.00), (143.73, 96.00), pad('J_OLED', 2)], width=1.4)

    # 8. Decoupling Caps C3, C4 to Pi 4 Power
    add_raw("/+5V_PWR", [pad('C4', 1), pad('C3', 1)], width=1.4)
    add_raw("/+5V_PWR", [pad('C3', 1), pad('U_PI4', 4)], width=1.4)
    add_raw("/+5V_PWR", [pad('U_PI4', 4), pad('U_PI4', 2)], width=1.4)
    add_raw("/GND", [pad('C4', 2), pad('C3', 2)], width=1.4)
    add_raw("/GND", [pad('C3', 2), pad('U_PI4', 6)], width=1.4)

    # 9. Ultrasonic US1
    add_raw("Net-(U_US1-ECHO)", [pad('U_US1', 3), (93.27, 52.00), (88.19, 52.00), pad('R1', 1)], width=1.0)
    add_raw("/ECHO_L", [pad('R1', 2), (95.81, 62.00), (88.19, 62.00), pad('R2', 1)], width=1.0)
    add_trace("/ECHO_L", [pad('R2', 1), (88.19, 74.00), (112.08, 74.00), pad('U_PI4', 13)], width=1.0)
    add_trace("/TRIG_L", [pad('U_US1', 2), (90.73, 50.00), (97.00, 50.00), (97.00, 76.50), (114.62, 76.50), pad('U_PI4', 11)], width=1.0)

    # 10. TCRT5000 Line Sensor
    add_trace("/LINE_R", [pad('U_PI4', 23), (99.38, 55.00), (103.46, 55.00), pad('U_LINE', 2)], width=1.0)
    add_trace("/LINE_C", [pad('U_PI4', 21), (101.92, 57.00), (106.00, 57.00), pad('U_LINE', 3)], width=1.0)
    add_trace("/LINE_L", [pad('U_PI4', 19), (104.46, 59.00), (108.54, 59.00), pad('U_LINE', 4)], width=1.0)

    # 11. Ultrasonic US2
    add_raw("Net-(U_US2-ECHO)", [pad('U_US2', 3), (121.27, 52.00), (116.19, 52.00), pad('R3', 1)], width=1.0)
    add_raw("/ECHO_R", [pad('R3', 2), (123.81, 62.00), (116.19, 62.00), pad('R4', 1)], width=1.0)

    # 12. Star Ground Primary Power Branch
    add_trace("/GND", [pad('U1', 2), (47.00, 88.00), (47.00, 42.00), pad('BT1', 2)], width=1.4)
    add_trace("/GND", [pad('BT1', 2), (53.00, 42.00), pad('C1', 2)], width=1.4)
    add_trace("/GND", [pad('C1', 2), (53.00, 63.00), (64.19, 63.00), pad('U_TB1', 11)], width=1.4)
    add_raw("/GND", [pad('U_TB1', 11), pad('U_TB1', 16)], width=1.4)
    add_raw("/GND", [pad('U_TB1', 16), pad('U_TB1', 8)], width=1.4)

    # Logic Ground to Pi 4
    add_trace("/GND", [pad('U1', 4), (58.00, 93.56), pad('U_PI4', 39)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 39), pad('U_PI4', 34)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 34), pad('U_PI4', 30)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 30), pad('U_PI4', 25)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 25), pad('U_PI4', 20)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 20), pad('U_PI4', 14)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 14), pad('U_PI4', 9)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 9), pad('U_PI4', 6)], width=1.4)

route_clean()
print(f"Total clean tracks: {len(tracks)}")

violations = check_clearance(tracks, world_pads, min_clearance=0.5)
print(f"Total geometry violations: {len(violations)}")
for v in violations:
    if v['type'] == 'track_pad_clearance':
        print(f"  Track-Pad: Track [{v['track_net']}] vs Pad {v['pad_ref']} [{v['pad_net']}] clearance={v['clearance']:.3f} mm at {v['pos']}")
    else:
        print(f"  Track-Track: [{v['net1']}] vs [{v['net2']}] clearance={v['clearance']:.3f} mm at {v['p1']} and {v['p2']}")
