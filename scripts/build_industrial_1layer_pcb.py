import math
import os
import re
import uuid

from load_footprints import fps

# =============================================================================
# 1. COMPONENT PLACEMENT DEFINITION
# =============================================================================
components = [
    # Ref, Val, FP, X, Y, Rot, SilkLabel
    ('BT1', 'BAT_3S2P_11.1V', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 50.00, 42.00, 0, 'BATT_12V'),
    ('SW1', 'SW_MAIN_10A', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 50.00, 56.00, 0, 'SW_MAIN'),
    ('F1', '7.5A_Blade', 'Fuseholder_Blade_Mini_Keystone_3568', 50.00, 70.00, 0, 'FUSE_7.5A'),
    ('U1', 'XL4015_Buck_5A', 'TerminalBlock_Phoenix_MKDS-1,5-4-5.08', 50.00, 88.00, 0, 'XL4015_5V'),
    ('C1', '470uF_25V', 'CP_Radial_D8.0mm_P3.50mm', 53.00, 48.00, 90, 'C1'),
    ('J_M1', 'MOTOR_FL', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 68.00, 45.00, 0, 'M1_FL'),
    ('J_M2', 'MOTOR_RL', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 77.00, 45.00, 0, 'M2_RL'),
    ('U_TB1', 'TB6612_Left', 'Module_TB6612FNG_Breakout', 68.00, 68.00, 270, 'TB6612_L'),
    ('U_US1', 'HC_SR04_Left', 'Sensor_HC_SR04', 92.00, 45.00, 0, 'US1_LEFT'),
    ('R1', '1k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 92.00, 58.00, 0, 'R1'),
    ('R2', '2k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 92.00, 66.00, 0, 'R2'),
    ('U_LINE', 'TCRT5000_3CH', 'Sensor_Line_TCRT5000_3CH', 106.00, 45.00, 180, 'LINE_3CH'),
    ('U_US2', 'HC_SR04_Right', 'Sensor_HC_SR04', 120.00, 45.00, 0, 'US2_RIGHT'),
    ('R3', '1k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 120.00, 58.00, 0, 'R3'),
    ('R4', '2k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 120.00, 66.00, 0, 'R4'),
    ('C2', '470uF_25V', 'CP_Radial_D8.0mm_P3.50mm', 133.00, 52.00, 90, 'C2'),
    ('J_M3', 'MOTOR_FR', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 140.00, 45.00, 0, 'M3_FR'),
    ('J_M4', 'MOTOR_RR', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 149.00, 45.00, 0, 'M4_RR'),
    ('U_TB2', 'TB6612_Right', 'Module_TB6612FNG_Breakout', 140.00, 68.00, 270, 'TB6612_R'),
    ('U_PI4', 'Raspberry_Pi_4_40Pin', 'PinSocket_2x20_P2.54mm_Vertical', 103.19, 94.83, 0, 'Rasp_PI4'),
    ('C3', '470uF_10V', 'CP_Radial_D6.3mm_P2.50mm', 126.00, 100.00, 0, 'C3'),
    ('C4', '100nF', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 119.00, 100.00, 0, 'C4'),
    ('J_OLED', 'OLED_1.3_I2C', 'Sensor_OLED_1.3', 145.00, 95.00, 0, 'OLED'),
    ('R_JMP1', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 130.00, 84.00, 270, 'J1 (0R)'),
    ('R_JMP2', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 133.50, 84.00, 270, 'J2 (0R)'),
    ('R_JMP3', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 137.00, 84.00, 270, 'J3 (0R)'),
    ('R_JMP4', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 114.00, 78.00, 0, 'J4 (0R)'),
    ('R_JMP5', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 122.00, 78.00, 0, 'J5 (0R)'),
    ('R_JMP6', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 130.00, 78.00, 0, 'J6 (0R)')
]

# Read project_netlist.net
with open('project_netlist.net', 'r', encoding='utf-8') as f:
    nl_text = f.read()

net_map = {}
net_names = []
net_blocks = re.findall(r'\(net\s+\(code\s+"\d+"\)\s+\(name\s+"([^"]+)"\)(.*?)(?=\(net\b|\)\s*\)\s*\Z)', nl_text, re.DOTALL)
for name, body in net_blocks:
    if name not in net_names:
        net_names.append(name)
    nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', body)
    for r, p in nodes:
        net_map[(r, p)] = name

net_id = {name: i + 1 for i, name in enumerate(net_names)}

def get_net_id(name):
    if name in net_id:
        return net_id[name]
    if '/' + name in net_id:
        return net_id['/' + name]
    return 0

def get_world(x0, y0, rot_deg, lx, ly):
    rad = math.radians(rot_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    wx = x0 + lx * cos_a - ly * sin_a
    wy = y0 + lx * sin_a + ly * cos_a
    return round(wx, 4), round(wy, 4)

world_pads = {}
for ref, val, fp_name, x0, y0, rot, silk in components:
    p_dict = fps[fp_name]
    world_pads[ref] = {}
    for p_num, p in p_dict.items():
        wx, wy = get_world(x0, y0, rot, p['lx'], p['ly'])
        n_name = net_map.get((ref, p_num), '')
        n_id = get_net_id(n_name)
        world_pads[ref][p_num] = {
            'x': wx, 'y': wy,
            'net_name': n_name,
            'net_id': n_id,
            'sx': p['sx'], 'sy': p['sy'],
            'drill': p['drill'],
            'shape': p['shape'],
            'type': p['type']
        }

def pad(ref, p_num):
    return (world_pads[ref][str(p_num)]['x'], world_pads[ref][str(p_num)]['y'])

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

# =============================================================================
# 2. DEFINITIVE PLANAR ROUTING IMPLEMENTATION
# =============================================================================
def route_definitive():
    tracks.clear()

    # --- 1. /BAT+ ---
    add_raw("/BAT+", [pad('BT1', 1), pad('SW1', 1)], width=1.4)

    # --- 2. /FUSE_IN ---
    add_trace("/FUSE_IN", [pad('SW1', 2), (54.54, 63.00), (46.00, 63.00), pad('F1', 1)], width=1.4)

    # --- 3. /VM_MOTOR ---
    # F1.2 to Buck U1.1
    add_trace("/VM_MOTOR", [pad('F1', 2), (56.00, 78.00), (42.38, 78.00), pad('U1', 1)], width=1.4)
    # F1.2 to TB6612 Left Pin 9
    add_trace("/VM_MOTOR", [pad('F1', 2), (56.00, 60.38), pad('U_TB1', 9)], width=1.4)
    # TB6612 Left Pin 9 to C1.1
    add_trace("/VM_MOTOR", [pad('U_TB1', 9), (59.11, 48.00), pad('C1', 1)], width=1.4)
    # C1.1 across Top Corridor (Y=39.00) to C2.1 and TB6612 Right Pin 9
    add_trace("/VM_MOTOR", [pad('C1', 1), (44.00, 48.00), (44.00, 39.00), (133.00, 39.00), pad('C2', 1)], width=1.4)
    add_trace("/VM_MOTOR", [pad('C2', 1), (133.00, 60.38), pad('U_TB2', 9)], width=1.4)

    # --- 4. Left Motor Outputs ---
    add_raw("/M1_A", [pad('U_TB1', 12), pad('J_M1', 1)], width=1.4)
    add_raw("/M1_B", [pad('U_TB1', 13), pad('J_M1', 2)], width=1.4)
    add_trace("/M2_B", [pad('U_TB1', 14), (71.81, 55.00), (74.46, 55.00), pad('J_M2', 1)], width=1.4)
    add_trace("/M2_A", [pad('U_TB1', 15), (74.35, 57.00), (79.54, 57.00), pad('J_M2', 2)], width=1.4)

    # --- 5. Right Motor Outputs ---
    add_raw("/M3_A", [pad('U_TB2', 12), pad('J_M3', 1)], width=1.4)
    add_raw("/M3_B", [pad('U_TB2', 13), pad('J_M3', 2)], width=1.4)
    add_trace("/M4_B", [pad('U_TB2', 14), (143.81, 55.00), (146.46, 55.00), pad('J_M4', 1)], width=1.4)
    add_trace("/M4_A", [pad('U_TB2', 15), (146.35, 57.00), (151.54, 57.00), pad('J_M4', 2)], width=1.4)

    # --- 6. Left Motor Control ---
    # Concentric U-loops inside module
    add_trace("/AIN1_L", [pad('U_TB1', 3), (64.19, 72.50), (69.27, 72.50), pad('U_TB1', 5)], width=1.0)
    add_trace("/AIN2_L", [pad('U_TB1', 2), (61.65, 69.50), (71.81, 69.50), pad('U_TB1', 6)], width=1.0)
    add_trace("/PWMA_L", [pad('U_TB1', 1), (59.11, 66.50), (74.35, 66.50), pad('U_TB1', 7)], width=1.0)
    # Direct from Pi 4 North Row
    add_trace("/AIN1_L", [pad('U_PI4', 37), (81.60, 83.00), (69.27, 83.00), pad('U_TB1', 5)], width=1.0)
    add_trace("/AIN2_L", [pad('U_PI4', 35), (84.14, 85.50), (71.81, 85.50), pad('U_TB1', 6)], width=1.0)
    add_trace("/PWMA_L", [pad('U_PI4', 33), (86.68, 88.00), (74.35, 88.00), pad('U_TB1', 7)], width=1.0)

    # --- 7. Right Motor Control ---
    # Concentric U-loops inside module
    add_trace("/AIN1_R", [pad('U_TB2', 3), (136.19, 72.50), (141.27, 72.50), pad('U_TB2', 5)], width=1.0)
    add_trace("/AIN2_R", [pad('U_TB2', 2), (133.65, 69.50), (143.81, 69.50), pad('U_TB2', 6)], width=1.0)
    add_trace("/PWMA_R", [pad('U_TB2', 1), (131.11, 66.50), (146.35, 66.50), pad('U_TB2', 7)], width=1.0)
    # Along South corridor (Y=104, 105.5, 107) to Jumpers Pad 1 (South side)
    add_trace("Net-(U_PI4-GPIO12_PWMB_R)", [pad('U_PI4', 32), (89.22, 104.00), (130.00, 104.00), pad('R_JMP1', 1)], width=1.0)
    add_trace("Net-(U_PI4-GPIO16_AIN1_R)", [pad('U_PI4', 36), (84.14, 105.50), (133.50, 105.50), pad('R_JMP2', 1)], width=1.0)
    add_trace("Net-(U_PI4-GPIO20_AIN2_R)", [pad('U_PI4', 38), (81.60, 107.00), (137.00, 107.00), pad('R_JMP3', 1)], width=1.0)
    # From Jumpers Pad 2 (North side) to U_TB2
    add_raw("/PWMA_R", [pad('R_JMP1', 2), pad('U_TB2', 1)], width=1.0)
    add_raw("/AIN1_R", [pad('R_JMP2', 2), (133.50, 77.00), (136.19, 77.00), pad('U_TB2', 3)], width=1.0)
    add_raw("/AIN2_R", [pad('R_JMP3', 2), (137.00, 78.50), (133.65, 78.50), pad('U_TB2', 2)], width=1.0)

    # --- 8. OLED Display (Straight East from Pi 4 Pins 1, 3, 5, 6 at Y=93.56/96.10) ---
    add_trace("/I2C_SDA", [pad('U_PI4', 3), (124.78, 92.50), (148.81, 92.50), pad('J_OLED', 4)], width=1.0)
    add_trace("/I2C_SCL", [pad('U_PI4', 5), (122.24, 91.00), (146.27, 91.00), pad('J_OLED', 3)], width=1.0)

    # --- 9. TCRT5000 Line Sensor (Straight Vertical) ---
    add_trace("/LINE_R", [pad('U_PI4', 23), (99.38, 55.00), (103.46, 55.00), pad('U_LINE', 2)], width=1.0)
    add_trace("/LINE_C", [pad('U_PI4', 21), (101.92, 57.00), (106.00, 57.00), pad('U_LINE', 3)], width=1.0)
    add_trace("/LINE_L", [pad('U_PI4', 19), (104.46, 59.00), (108.54, 59.00), pad('U_LINE', 4)], width=1.0)

    # --- 10. Ultrasonic Sensors US1 & US2 ---
    add_raw("Net-(U_US1-ECHO)", [pad('U_US1', 3), (93.27, 52.00), (88.19, 52.00), pad('R1', 1)], width=1.0)
    add_raw("/ECHO_L", [pad('R1', 2), (95.81, 62.00), (88.19, 62.00), pad('R2', 1)], width=1.0)
    add_trace("/ECHO_L", [pad('R2', 1), (88.19, 74.00), (112.08, 74.00), pad('U_PI4', 13)], width=1.0)
    add_trace("/TRIG_L", [pad('U_US1', 2), (90.73, 50.00), (97.00, 50.00), (97.00, 76.50), (114.62, 76.50), pad('U_PI4', 11)], width=1.0)

    add_raw("Net-(U_US2-ECHO)", [pad('U_US2', 3), (121.27, 52.00), (116.19, 52.00), pad('R3', 1)], width=1.0)
    add_raw("/ECHO_R", [pad('R3', 2), (123.81, 62.00), (116.19, 62.00), pad('R4', 1)], width=1.0)
    add_trace("/ECHO_R", [pad('R4', 1), (116.19, 71.50), (107.00, 71.50), (107.00, 93.00), pad('U_PI4', 18)], width=1.0)
    add_trace("/TRIG_R", [pad('U_US2', 2), (118.73, 50.00), (109.54, 50.00), pad('U_PI4', 16)], width=1.0)

    # --- 11. Power Net: +5V_PWR ---
    add_trace("/+5V_PWR", [pad('U1', 3), (54.54, 91.00), (62.00, 91.00), (62.00, 98.00), (116.50, 98.00), pad('C4', 1)], width=1.4)
    add_raw("/+5V_PWR", [pad('C4', 1), pad('C3', 1)], width=1.4)
    add_raw("/+5V_PWR", [pad('C3', 1), pad('U_PI4', 4)], width=1.4)
    add_raw("/+5V_PWR", [pad('U_PI4', 4), pad('U_PI4', 2)], width=1.4)
    add_trace("/+5V_PWR", [pad('U_PI4', 2), (127.32, 85.00), (117.81, 85.00), pad('R_JMP4', 2)], width=1.4)
    add_trace("/+5V_PWR", [pad('R_JMP4', 1), (110.19, 78.00), (88.19, 78.00), pad('U_US1', 1)], width=1.4)
    add_trace("/+5V_PWR", [pad('R_JMP4', 2), (117.81, 75.00), (116.19, 75.00), pad('U_US2', 1)], width=1.4)

    # --- 12. Logic Supply: +3V3_LOGIC ---
    add_trace("/+3V3_LOGIC", [pad('U_PI4', 1), (127.32, 94.00), (141.19, 94.00), pad('J_OLED', 1)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('U_PI4', 1), (127.32, 82.50), (125.81, 82.50), pad('R_JMP5', 2)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('R_JMP5', 1), (118.19, 78.00), (111.08, 78.00), pad('U_LINE', 5)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('R_JMP5', 1), (118.19, 81.00), (66.73, 81.00), pad('U_TB1', 4)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('U_TB1', 4), (66.73, 63.50), (61.65, 63.50), pad('U_TB1', 10)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('R_JMP5', 2), (125.81, 80.50), (138.73, 80.50), pad('U_TB2', 4)], width=1.4)
    add_trace("/+3V3_LOGIC", [pad('U_TB2', 4), (138.73, 63.50), (133.65, 63.50), pad('U_TB2', 10)], width=1.4)

    # --- 13. Ground Net: GND (Star-Ground Topology) ---
    add_trace("/GND", [pad('U1', 2), (48.00, 88.00), (48.00, 42.00), pad('BT1', 2)], width=1.4)
    add_trace("/GND", [pad('BT1', 2), (53.00, 42.00), pad('C1', 2)], width=1.4)
    add_trace("/GND", [pad('C1', 2), (53.00, 63.00), (64.19, 63.00), pad('U_TB1', 11)], width=1.4)
    add_raw("/GND", [pad('U_TB1', 11), pad('U_TB1', 16)], width=1.4)
    add_raw("/GND", [pad('U_TB1', 16), pad('U_TB1', 8)], width=1.4)

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

    add_trace("/GND", [pad('U_PI4', 6), (122.24, 85.00), (126.19, 85.00), pad('R_JMP6', 1)], width=1.4)
    add_trace("/GND", [pad('R_JMP6', 2), (133.81, 78.00), (148.89, 78.00), pad('U_TB2', 8)], width=1.4)
    add_raw("/GND", [pad('U_TB2', 8), pad('U_TB2', 16)], width=1.4)
    add_raw("/GND", [pad('U_TB2', 16), pad('U_TB2', 11)], width=1.4)
    add_trace("/GND", [pad('U_TB2', 11), (136.19, 53.75), pad('C2', 2)], width=1.4)

    add_trace("/GND", [pad('R_JMP6', 1), (126.19, 70.00), (95.81, 70.00), pad('R2', 2)], width=1.4)
    add_raw("/GND", [pad('R2', 2), pad('U_US1', 4)], width=1.4)
    add_trace("/GND", [pad('R_JMP6', 2), (133.81, 70.00), (123.81, 70.00), pad('R4', 2)], width=1.4)
    add_raw("/GND", [pad('R4', 2), pad('U_US2', 4)], width=1.4)
    add_trace("/GND", [pad('U_US2', 4), (123.81, 48.00), (100.92, 48.00), pad('U_LINE', 1)], width=1.4)

route_definitive()
print(f"Total track segments: {len(tracks)}")

# =============================================================================
# 3. WRITE KICAD PCB FILE
# =============================================================================
def write_pcb(filepath):
    lines = []
    lines.append('(kicad_pcb')
    lines.append('\t(version 20260206)')
    lines.append('\t(generator "pcbnew")')
    lines.append('\t(generator_version "10.0")')
    lines.append('\t(general')
    lines.append('\t\t(thickness 1.6)')
    lines.append('\t\t(legacy_teardrops no)')
    lines.append('\t)')
    lines.append('\t(paper "A4")')
    lines.append('\t(layers')
    lines.append('\t\t(0 "F.Cu" signal)')
    lines.append('\t\t(2 "B.Cu" signal)')
    lines.append('\t\t(9 "F.Adhes" user "F.Adhesive")')
    lines.append('\t\t(11 "B.Adhes" user "B.Adhesive")')
    lines.append('\t\t(13 "F.Paste" user)')
    lines.append('\t\t(15 "B.Paste" user)')
    lines.append('\t\t(5 "F.SilkS" user "F.Silkscreen")')
    lines.append('\t\t(7 "B.SilkS" user "B.Silkscreen")')
    lines.append('\t\t(1 "F.Mask" user)')
    lines.append('\t\t(3 "B.Mask" user)')
    lines.append('\t\t(17 "Dwgs.User" user "User.Drawings")')
    lines.append('\t\t(19 "Cmts.User" user "User.Comments")')
    lines.append('\t\t(21 "Eco1.User" user "User.Eco1")')
    lines.append('\t\t(23 "Eco2.User" user "User.Eco2")')
    lines.append('\t\t(25 "Edge.Cuts" user)')
    lines.append('\t\t(27 "Margin" user)')
    lines.append('\t\t(31 "F.CrtYd" user "F.Courtyard")')
    lines.append('\t\t(29 "B.CrtYd" user "B.Courtyard")')
    lines.append('\t\t(35 "F.Fab" user)')
    lines.append('\t\t(33 "B.Fab" user)')
    lines.append('\t)')
    lines.append('\t(setup')
    lines.append('\t\t(pad_to_mask_clearance 0)')
    lines.append('\t\t(solder_mask_min_width 0.15)')
    lines.append('\t\t(pcbplotparams')
    lines.append('\t\t\t(layerselection 0x00000000_00000000_55555555_5755f5ff)')
    lines.append('\t\t\t(plot_black_and_white yes)')
    lines.append('\t\t\t(outputformat 1)')
    lines.append('\t\t)')
    lines.append('\t)')

    # Net definitions
    lines.append('\t(net 0 "")')
    for name in net_names:
        nid = net_id[name]
        lines.append(f'\t(net {nid} "{name}")')

    # Netclass definitions
    lines.append('\t(net_class "Default"')
    lines.append('\t\t(clearance 0.5)')
    lines.append('\t\t(trace_width 1.0)')
    lines.append('\t\t(via_dia 2.0)')
    lines.append('\t\t(via_drill 0.8)')
    for name in net_names:
        lines.append(f'\t\t(add_net "{name}")')
    lines.append('\t)')

    # Footprints
    for ref, val, fp_name, x0, y0, rot, silk in components:
        fp_file = os.path.join('libraries/robot_electronics.pretty', fp_name + '.kicad_mod')
        with open(fp_file, 'r', encoding='utf-8') as f:
            fp_raw = f.read()
        
        # Parse footprint body
        rot_str = f" {rot}" if rot else ""
        fp_out = f'\t(footprint "robot_electronics:{fp_name}"\n'
        fp_out += f'\t\t(layer "F.Cu")\n'
        fp_out += f'\t\t(uuid "{uuid.uuid4()}")\n'
        fp_out += f'\t\t(at {x0:.2f} {y0:.2f}{rot_str})\n'
        fp_out += f'\t\t(property "Reference" "{ref}" (at 0 -3.5 0) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness 0.15))))\n'
        fp_out += f'\t\t(property "Value" "{silk}" (at 0 3.5 0) (layer "F.Fab") (effects (font (size 1.2 1.2) (thickness 0.15))))\n'
        
        # Extract pads from footprint raw
        pad_matches = re.finditer(r'\(pad\s+"([^"]+)"\s+(thru_hole|smd)\s+(\w+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)\s*\(size\s+([-\d.]+)\s+([-\d.]+)\)\s*\(drill\s+([-\d.]+)\)?\s*\(layers\s+"([^"]+)"\s+"([^"]+)"\)', fp_raw)
        for pm in pad_matches:
            p_num = pm.group(1)
            p_type = pm.group(2)
            shape = pm.group(3)
            lx = float(pm.group(4))
            ly = float(pm.group(5))
            lrot = pm.group(6)
            sx = float(pm.group(7))
            sy = float(pm.group(8))
            drill = float(pm.group(9))
            l1 = pm.group(10)
            l2 = pm.group(11)
            
            p_net_name = net_map.get((ref, p_num), '')
            p_net_id = get_net_id(p_net_name)
            
            lrot_str = f" {lrot}" if lrot else ""
            net_clause = f' (net {p_net_id} "{p_net_name}")' if p_net_name else ''
            
            fp_out += f'\t\t(pad "{p_num}" {p_type} {shape} (at {lx:.2f} {ly:.2f}{lrot_str}) (size {sx:.2f} {sy:.2f}) (drill {drill:.2f}) (layers "{l1}" "{l2}"){net_clause})\n'
        
        fp_out += '\t)'
        lines.append(fp_out)

    # Tracks on B.Cu
    for t in tracks:
        p1, p2 = t['p1'], t['p2']
        w = t['width']
        nid = t['net_id']
        nname = t['net']
        lines.append(f'\t(segment (start {p1[0]:.4f} {p1[1]:.4f}) (end {p2[0]:.4f} {p2[1]:.4f}) (width {w:.2f}) (layer "B.Cu") (net {nid}) (uuid "{uuid.uuid4()}"))')

    # Board Outline (Edge.Cuts) - Closed Rectangle
    # X from 40.0 to 157.0 (117mm), Y from 36.0 to 110.0 (74mm)
    lines.append('\t(gr_line (start 40.00 36.00) (end 157.00 36.00) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (uuid "' + str(uuid.uuid4()) + '"))')
    lines.append('\t(gr_line (start 157.00 36.00) (end 157.00 110.00) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (uuid "' + str(uuid.uuid4()) + '"))')
    lines.append('\t(gr_line (start 157.00 110.00) (end 40.00 110.00) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (uuid "' + str(uuid.uuid4()) + '"))')
    lines.append('\t(gr_line (start 40.00 110.00) (end 40.00 36.00) (stroke (width 0.15) (type solid)) (layer "Edge.Cuts") (uuid "' + str(uuid.uuid4()) + '"))')

    lines.append(')')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Successfully written PCB file: {filepath}")

write_pcb('Pi4_Robot_Carrier_1Layer.kicad_pcb')
write_pcb('robot_electronics.kicad_pcb')

