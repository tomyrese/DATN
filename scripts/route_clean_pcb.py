import math
import os
import re
import uuid

from init_world_pads import world_pads, net_id, components, net_map

def pad(ref, p_num):
    p = world_pads[ref][str(p_num)]
    return (p['x'], p['y'])

def get_net_id(name):
    if name in net_id:
        return net_id[name]
    if '/' + name in net_id:
        return net_id['/' + name]
    return 0

def chamfer_path(pts, d=1.2):
    if len(pts) <= 2: return list(pts)
    result = [pts[0]]
    for i in range(1, len(pts) - 1):
        p_prev, p_curr, p_next = pts[i - 1], pts[i], pts[i + 1]
        dx1, dy1 = p_curr[0] - p_prev[0], p_curr[1] - p_prev[1]
        len1 = math.hypot(dx1, dy1)
        dx2, dy2 = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
        len2 = math.hypot(dx2, dy2)
        if len1 < 1e-4 or len2 < 1e-4: continue
        ux1, uy1 = dx1 / len1, dy1 / len1
        ux2, uy2 = dx2 / len2, dy2 / len2
        dot = ux1 * ux2 + uy1 * uy2
        if abs(dot) < 0.25: # roughly 90 degree turn
            actual_d = min(d, len1 * 0.40, len2 * 0.40)
            p_in = (round(p_curr[0] - ux1 * actual_d, 4), round(p_curr[1] - uy1 * actual_d, 4))
            p_out = (round(p_curr[0] + ux2 * actual_d, 4), round(p_curr[1] + uy2 * actual_d, 4))
            result.append(p_in); result.append(p_out)
        else:
            result.append(p_curr)
    result.append(pts[-1])
    return result

tracks = []
def add_trace(net, pts, width=1.0, d=1.2):
    c_pts = chamfer_path(pts, d=d)
    nid = get_net_id(net)
    canonical = net if net.startswith('/') or net.startswith('Net-') else '/' + net
    for i in range(len(c_pts) - 1):
        tracks.append({
            'net': canonical,
            'net_id': nid,
            'p1': c_pts[i],
            'p2': c_pts[i+1],
            'width': width
        })

def add_raw(net, pts, width=1.0):
    nid = get_net_id(net)
    canonical = net if net.startswith('/') or net.startswith('Net-') else '/' + net
    for i in range(len(pts) - 1):
        tracks.append({
            'net': canonical,
            'net_id': nid,
            'p1': pts[i],
            'p2': pts[i+1],
            'width': width
        })

def route_all():
    tracks.clear()

    # 1. /BAT+
    add_raw("/BAT+", [pad('BT1', 1), pad('SW1', 1)], width=1.4)

    # 2. /FUSE_IN
    add_trace("/FUSE_IN", [pad('SW1', 2), (54.54, 63.00), (48.00, 63.00), pad('F1', 1)], width=1.4)

    # 3. /VM_MOTOR
    add_trace("/VM_MOTOR", [pad('F1', 2), (56.00, 78.00), (44.38, 78.00), pad('U1', 1)], width=1.4)
    add_trace("/VM_MOTOR", [pad('F1', 2), (56.00, 60.38), pad('U_TB1', 9)], width=1.4)
    add_trace("/VM_MOTOR", [pad('U_TB1', 9), (59.11, 52.00), pad('C1', 1)], width=1.4)
    add_trace("/VM_MOTOR", [pad('C1', 1), (54.25, 39.50), (131.25, 39.50), pad('C2', 1)], width=1.4)
    add_trace("/VM_MOTOR", [pad('C2', 1), pad('U_TB2', 9)], width=1.4)

    # 4. Left Motor Outputs
    add_raw("/M1_A", [pad('U_TB1', 12), pad('J_M1', 1)], width=1.4)
    add_raw("/M1_B", [pad('U_TB1', 13), pad('J_M1', 2)], width=1.4)
    add_trace("/M2_B", [pad('U_TB1', 14), (71.81, 55.00), (74.46, 55.00), pad('J_M2', 1)], width=1.4)
    add_trace("/M2_A", [pad('U_TB1', 15), (74.35, 57.00), (79.54, 57.00), pad('J_M2', 2)], width=1.4)

    # 5. Right Motor Outputs
    add_raw("/M3_A", [pad('U_TB2', 12), pad('J_M3', 1)], width=1.4)
    add_raw("/M3_B", [pad('U_TB2', 13), pad('J_M3', 2)], width=1.4)
    add_trace("/M4_B", [pad('U_TB2', 14), (143.81, 55.00), (146.46, 55.00), pad('J_M4', 1)], width=1.4)
    add_trace("/M4_A", [pad('U_TB2', 15), (146.35, 57.00), (151.54, 57.00), pad('J_M4', 2)], width=1.4)

    # 6. Left Motor Control (Internal U-loops)
    add_trace("/AIN1_L", [pad('U_TB1', 3), (64.19, 72.50), (69.27, 72.50), pad('U_TB1', 5)], width=1.0)
    add_trace("/AIN2_L", [pad('U_TB1', 2), (61.65, 69.50), (71.81, 69.50), pad('U_TB1', 6)], width=1.0)
    add_trace("/PWMA_L", [pad('U_TB1', 1), (59.11, 66.50), (74.35, 66.50), pad('U_TB1', 7)], width=1.0)

    # Left Motor Control (from Pi 4)
    add_trace("/AIN1_L", [pad('U_PI4', 37), (81.60, 83.00), (69.27, 83.00), pad('U_TB1', 5)], width=1.0)
    add_trace("/AIN2_L", [pad('U_PI4', 35), (84.14, 85.50), (71.81, 85.50), pad('U_TB1', 6)], width=1.0)
    add_trace("/PWMA_L", [pad('U_PI4', 33), (86.68, 88.00), (74.35, 88.00), pad('U_TB1', 7)], width=1.0)

    # 7. Right Motor Control (Internal U-loops)
    add_trace("/AIN1_R", [pad('U_TB2', 3), (136.19, 72.50), (141.27, 72.50), pad('U_TB2', 5)], width=1.0)
    add_trace("/AIN2_R", [pad('U_TB2', 2), (133.65, 69.50), (143.81, 69.50), pad('U_TB2', 6)], width=1.0)
    add_trace("/PWMA_R", [pad('U_TB2', 1), (131.11, 66.50), (146.35, 66.50), pad('U_TB2', 7)], width=1.0)

    # Right Motor Control (from Pi 4 through Jumpers)
    add_trace("Net-(U_PI4-GPIO12_PWMB_R)", [pad('U_PI4', 32), (89.22, 100.00), (131.00, 100.00), pad('R_JMP1', 2)], width=1.0)
    add_trace("Net-(U_PI4-GPIO16_AIN1_R)", [pad('U_PI4', 36), (84.14, 102.50), (136.00, 102.50), pad('R_JMP2', 2)], width=1.0)
    add_trace("Net-(U_PI4-GPIO20_AIN2_R)", [pad('U_PI4', 38), (81.60, 105.00), (141.00, 105.00), pad('R_JMP3', 2)], width=1.0)

    # From Jumpers to TB6612 Right
    add_raw("/PWMA_R", [pad('R_JMP1', 1), pad('U_TB2', 1)], width=1.0)
    add_raw("/AIN1_R", [pad('R_JMP2', 1), pad('U_TB2', 3)], width=1.0)
    add_raw("/AIN2_R", [pad('R_JMP3', 1), (141.00, 78.50), (133.65, 78.50), pad('U_TB2', 2)], width=1.0)

    # 8. OLED Display
    add_trace("/I2C_SDA", [pad('U_PI4', 3), (124.78, 89.50), (148.81, 89.50), pad('J_OLED', 4)], width=1.0)
    add_trace("/I2C_SCL", [pad('U_PI4', 5), (122.24, 87.00), (146.27, 87.00), pad('J_OLED', 3)], width=1.0)

    # 9. TCRT5000 Line Sensor
    add_trace("/LINE_R", [pad('U_PI4', 23), (99.38, 55.00), (103.46, 55.00), pad('U_LINE', 2)], width=1.0)
    add_trace("/LINE_C", [pad('U_PI4', 21), (101.92, 57.00), (106.00, 57.00), pad('U_LINE', 3)], width=1.0)
    add_trace("/LINE_L", [pad('U_PI4', 19), (104.46, 59.00), (108.54, 59.00), pad('U_LINE', 4)], width=1.0)

    # 10. Ultrasonic Sensors US1 & US2
    add_raw("Net-(U_US1-ECHO)", [pad('U_US1', 3), (93.27, 52.00), (88.19, 52.00), pad('R1', 1)], width=1.0)
    add_raw("/ECHO_L", [pad('R1', 2), (95.81, 62.00), (88.19, 62.00), pad('R2', 1)], width=1.0)
    add_trace("/ECHO_L", [pad('R2', 1), (88.19, 74.00), (112.08, 74.00), pad('U_PI4', 13)], width=1.0)
    add_trace("/TRIG_L", [pad('U_US1', 2), (90.73, 50.00), (97.00, 50.00), (97.00, 76.50), (114.62, 76.50), pad('U_PI4', 11)], width=1.0)

    add_raw("Net-(U_US2-ECHO)", [pad('U_US2', 3), (121.27, 52.00), (116.19, 52.00), pad('R3', 1)], width=1.0)
    add_raw("/ECHO_R", [pad('R3', 2), (123.81, 62.00), (116.19, 62.00), pad('R4', 1)], width=1.0)
    add_trace("/ECHO_R", [pad('R4', 1), (116.19, 71.50), (107.00, 71.50), (107.00, 93.00), pad('U_PI4', 18)], width=1.0)
    add_trace("/TRIG_R", [pad('U_US2', 2), (118.73, 50.00), (109.54, 50.00), pad('U_PI4', 16)], width=1.0)

    # 11. Power Net: +5V_PWR
    # Pi 4 Power input
    add_trace("/+5V_PWR", [pad('U1', 3), (54.54, 91.00), (62.00, 91.00), (62.00, 98.50), (116.50, 98.50), pad('C4', 1)], width=1.4)
    add_raw("/+5V_PWR", [pad('C4', 1), pad('C3', 1)], width=1.4)
    add_raw("/+5V_PWR", [pad('C3', 1), pad('U_PI4', 4)], width=1.4)
    add_raw("/+5V_PWR", [pad('U_PI4', 4), pad('U_PI4', 2)], width=1.4)

    # Sensor +5V Power via R_JMP4
    add_trace("/+5V_PWR", [pad('U_PI4', 2), (127.32, 85.00), (117.81, 85.00), pad('R_JMP4', 2)], width=1.4)
    add_trace("/+5V_PWR", [pad('R_JMP4', 1), (110.19, 78.00), (88.19, 78.00), pad('U_US1', 1)], width=1.4)
    add_trace("/+5V_PWR", [pad('R_JMP4', 2), (117.81, 75.00), (116.19, 75.00), pad('U_US2', 1)], width=1.4)

    # 12. Logic Supply: +3V3_LOGIC
    add_trace("/+3V3_LOGIC", [pad('U_PI4', 1), (127.32, 92.00), (141.19, 92.00), pad('J_OLED', 1)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('U_PI4', 1), (127.32, 82.50), (125.81, 82.50), pad('R_JMP5', 2)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('R_JMP5', 1), (118.19, 78.00), (111.08, 78.00), pad('U_LINE', 5)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('R_JMP5', 1), (118.19, 81.00), (66.73, 81.00), pad('U_TB1', 4)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('U_TB1', 4), (66.73, 63.50), (61.65, 63.50), pad('U_TB1', 10)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('R_JMP5', 2), (125.81, 80.50), (138.73, 80.50), pad('U_TB2', 4)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('U_TB2', 4), (138.73, 63.50), (133.65, 63.50), pad('U_TB2', 10)], width=1.4)

    # 13. Ground Net: GND (Star-Ground Topology)
    # Power GND branch to Battery, Buck, Left Motor, C1
    add_raw("/GND", [pad('U1', 2), pad('BT1', 2)], width=1.4)
    add_trace("/GND", [pad('U1', 2), (49.46, 52.00), pad('C1', 2)], width=1.4)
    add_trace("/GND", [pad('C1', 2), (57.75, 63.00), (64.19, 63.00), pad('U_TB1', 11)], width=1.4)
    add_raw("/GND", [pad('U_TB1', 11), pad('U_TB1', 16)], width=1.4)
    add_raw("/GND", [pad('U_TB1', 16), pad('U_TB1', 8)], width=1.4)

    # Logic GND branch to Pi 4
    add_trace("/GND", [pad('U1', 4), (59.62, 93.56), pad('U_PI4', 39)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 39), pad('U_PI4', 34)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 34), pad('U_PI4', 30)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 30), pad('U_PI4', 25)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 25), pad('U_PI4', 20)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 20), pad('U_PI4', 14)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 14), pad('U_PI4', 9)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 9), pad('U_PI4', 6)], width=1.4)
    add_raw("/GND", [pad('U_PI4', 6), pad('C4', 2)], width=1.4)
    add_raw("/GND", [pad('C4', 2), pad('C3', 2)], width=1.4)
    add_trace("/GND", [pad('C3', 2), (127.25, 96.00), (143.73, 96.00), pad('J_OLED', 2)], width=1.4)

    # Right Side GND branch via R_JMP6
    add_trace("/GND", [pad('U_PI4', 6), (122.24, 85.00), (126.19, 85.00), pad('R_JMP6', 1)], width=1.4)
    add_trace("/GND", [pad('R_JMP6', 2), (133.81, 78.00), (148.89, 78.00), pad('U_TB2', 8)], width=1.4)
    add_raw("/GND", [pad('U_TB2', 8), pad('U_TB2', 16)], width=1.4)
    add_raw("/GND", [pad('U_TB2', 16), pad('U_TB2', 11)], width=1.4)
    add_trace("/GND", [pad('U_TB2', 11), (136.19, 52.00), pad('C2', 2)], width=1.4)

    # Sensor GND connections
    add_trace("/GND", [pad('R_JMP6', 1), (126.19, 70.00), (95.81, 70.00), pad('R2', 2)], width=1.4)
    add_raw("/GND", [pad('R2', 2), pad('U_US1', 4)], width=1.4)
    add_trace("/GND", [pad('R_JMP6', 2), (133.81, 70.00), (123.81, 70.00), pad('R4', 2)], width=1.4)
    add_raw("/GND", [pad('R4', 2), pad('U_US2', 4)], width=1.4)
    add_trace("/GND", [pad('U_US2', 4), (123.81, 48.00), (100.92, 48.00), pad('U_LINE', 1)], width=1.4)

    print(f"Total track segments routed: {len(tracks)}")

if __name__ == '__main__':
    route_all()
