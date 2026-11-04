import math
from load_footprints import fps
from geometry_checker import check_clearance

# Component definitions
components = [
    # Ref, Val, FP, X, Y, Rot, SilkLabel, SilkRefPos, SilkValPos
    ('BT1', 'BAT_3S2P_11.1V', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 50.00, 42.00, 0, 'BATT_12V', (0, -3.5), (0, 3.5)),
    ('SW1', 'SW_MAIN_10A', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 50.00, 56.00, 0, 'SW_MAIN', (0, -3.5), (0, 3.5)),
    ('F1', '7.5A_Blade', 'Fuseholder_Blade_Mini_Keystone_3568', 50.00, 70.00, 0, 'FUSE_7.5A', (0, -3.5), (0, 3.5)),
    ('U1', 'XL4015_Buck_5A', 'TerminalBlock_Phoenix_MKDS-1,5-4-5.08', 50.00, 88.00, 0, 'XL4015_5V', (0, -3.5), (0, 3.5)),
    ('C1', '470uF_25V', 'CP_Radial_D8.0mm_P3.50mm', 53.00, 48.00, 90, 'C1', (-3.5, 0), (3.5, 0)),
    ('J_M1', 'MOTOR_FL', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 68.00, 45.00, 0, 'M1_FL', (0, -3.5), (0, 3.5)),
    ('J_M2', 'MOTOR_RL', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 77.00, 45.00, 0, 'M2_RL', (0, -3.5), (0, 3.5)),
    ('U_TB1', 'TB6612_Left', 'Module_TB6612FNG_Breakout', 68.00, 68.00, 270, 'TB6612_L', (0, -11.0), (0, 11.0)),
    ('U_US1', 'HC_SR04_Left', 'Sensor_HC_SR04', 92.00, 45.00, 0, 'US1_LEFT', (0, -3.5), (0, 3.5)),
    ('R1', '1k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 92.00, 58.00, 0, 'R1', (0, -2.5), (0, 2.5)),
    ('R2', '2k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 92.00, 66.00, 0, 'R2', (0, -2.5), (0, 2.5)),
    ('U_LINE', 'TCRT5000_3CH', 'Sensor_Line_TCRT5000_3CH', 106.00, 45.00, 180, 'LINE_3CH', (0, -3.5), (0, 3.5)),
    ('U_US2', 'HC_SR04_Right', 'Sensor_HC_SR04', 120.00, 45.00, 0, 'US2_RIGHT', (0, -3.5), (0, 3.5)),
    ('R3', '1k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 120.00, 58.00, 0, 'R3', (0, -2.5), (0, 2.5)),
    ('R4', '2k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 120.00, 66.00, 0, 'R4', (0, -2.5), (0, 2.5)),
    ('C2', '470uF_25V', 'CP_Radial_D8.0mm_P3.50mm', 133.00, 52.00, 90, 'C2', (3.5, 0), (-3.5, 0)),
    ('J_M3', 'MOTOR_FR', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 140.00, 45.00, 0, 'M3_FR', (0, -3.5), (0, 3.5)),
    ('J_M4', 'MOTOR_RR', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 149.00, 45.00, 0, 'M4_RR', (0, -3.5), (0, 3.5)),
    ('U_TB2', 'TB6612_Right', 'Module_TB6612FNG_Breakout', 140.00, 68.00, 270, 'TB6612_R', (0, -11.0), (0, 11.0)),
    ('U_PI4', 'Raspberry_Pi_4_40Pin', 'PinSocket_2x20_P2.54mm_Vertical', 103.19, 94.83, 0, 'Rasp_PI4', (0, -3.5), (0, 3.5)),
    ('C3', '470uF_10V', 'CP_Radial_D6.3mm_P2.50mm', 126.00, 102.50, 0, 'C3', (0, 3.5), (0, -3.5)),
    ('C4', '100nF', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 119.00, 102.50, 0, 'C4', (0, 3.5), (0, -3.5)),
    ('J_OLED', 'OLED_1.3_I2C', 'Sensor_OLED_1.3', 145.00, 95.00, 0, 'OLED', (0, -3.5), (0, 3.5)),
    ('R_JMP1', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 129.50, 84.00, 270, 'J1 (0R)', (-2.2, 0), (2.2, 0)),
    ('R_JMP2', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 133.50, 84.00, 270, 'J2 (0R)', (-2.2, 0), (2.2, 0)),
    ('R_JMP3', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 137.50, 84.00, 270, 'J3 (0R)', (-2.2, 0), (2.2, 0)),
    ('R_JMP4', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 114.00, 78.00, 0, 'J4 (0R)', (0, -2.5), (0, 2.5)),
    ('R_JMP5', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 122.00, 78.00, 0, 'J5 (0R)', (0, -2.5), (0, 2.5)),
    ('R_JMP6', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 130.00, 78.00, 0, 'J6 (0R)', (0, -2.5), (0, 2.5))
]

# Read project_netlist.net
with open('project_netlist.net', 'r', encoding='utf-8') as f:
    nl_text = f.read()

import re
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
for item in components:
    ref, val, fp_name, x0, y0, rot, silk, sref, sval = item
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

print("Helper ready.")
