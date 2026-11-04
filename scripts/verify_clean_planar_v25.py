import math
import json

# Load world pads
with open('scripts/world_pads_actual.json', 'r', encoding='utf-8') as f:
    world_data = json.load(f)

def get_pad(ref, pad_num):
    return tuple(world_data[ref]['pads'][str(pad_num)]['world'])

def get_net(ref, pad_num):
    return world_data[ref]['pads'][str(pad_num)]['net']

# Helper chamfer
def chamfer_path(pts, d=1.5):
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
        if abs(dot) < 0.25: # ~90 deg
            actual_d = min(d, len1 * 0.40, len2 * 0.40)
            p_in = (round(p_curr[0] - ux1 * actual_d, 4), round(p_curr[1] - uy1 * actual_d, 4))
            p_out = (round(p_curr[0] + ux2 * actual_d, 4), round(p_curr[1] + uy2 * actual_d, 4))
            result.append(p_in); result.append(p_out)
        else:
            result.append(p_curr)
    result.append(pts[-1])
    return result

paths = []
def add_chamfered(net, pts, width=1.0, d=1.5):
    c_pts = chamfer_path(pts, d=d)
    for i in range(len(c_pts) - 1):
        paths.append({'net': net, 'p1': c_pts[i], 'p2': c_pts[i+1], 'width': width})

def add_raw(net, pts, width=1.0):
    for i in range(len(pts) - 1):
        paths.append({'net': net, 'p1': pts[i], 'p2': pts[i+1], 'width': width})

jumpers = []
def add_jumper(name, net, p1, p2):
    jumpers.append({'name': name, 'net': net, 'p1': p1, 'p2': p2})

def pt_pt_dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def pt_seg_dist(p, a, b):
    abx, aby = b[0] - a[0], b[1] - a[1]
    apx, apy = p[0] - a[0], p[1] - a[1]
    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq < 1e-8:
        return math.hypot(apx, apy)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab_len_sq))
    proj_x = a[0] + t * abx
    proj_y = a[1] + t * aby
    return math.hypot(p[0] - proj_x, p[1] - proj_y)

def seg_seg_dist(a, b, c, d):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    def intersect(A, B, C, D):
        return (ccw(A,C,D) != ccw(B,C,D)) and (ccw(A,B,C) != ccw(A,B,D))
    if intersect(a, b, c, d):
        return 0.0
    return min(
        pt_seg_dist(a, c, d),
        pt_seg_dist(b, c, d),
        pt_seg_dist(c, a, b),
        pt_seg_dist(d, a, b)
    )

def route_all():
    paths.clear()
    jumpers.clear()

    # =========================================================================
    # 1. MOTOR CONNECTIONS (Direct North)
    # =========================================================================
    # M1: TB1 Pad 13 (66.42, 61.21) -> Motor1 Pad 1 (66.41, 53.40) (/M1_A or M1_B)
    # Check nets of Motor 1: Pad 1 is /M1_A, Pad 2 is /M1_B
    # Check nets of TB1 North: Pad 12 is /M1_A (68.96), Pad 13 is /M1_B (66.42)
    # In .bak:
    # (66.41, 53.40) went straight to (66.42, 61.21)
    # (68.95, 53.40) went straight to (68.96, 61.21)
    # Both are 100% straight vertical!
    add_chamfered(get_net('LEFT', 13), [get_pad('LEFT', 13), get_pad('MOTOR1', 1)], width=1.0, d=1.0)
    add_chamfered(get_net('LEFT', 12), [get_pad('LEFT', 12), get_pad('MOTOR1', 2)], width=1.0, d=1.0)

    # M2:
    # TB1 Pad 14 (63.88, 61.21) -> Motor 2 Pad 1 (75.53, 53.44) (/M2_B)
    # TB1 Pad 15 (61.34, 61.21) -> Motor 2 Pad 2 (78.07, 53.44) (/M2_A)
    add_chamfered(get_net('LEFT', 14), [
        get_pad('LEFT', 14),
        (63.88, 56.50),
        (75.53, 56.50),
        get_pad('MOTOR2', 1)
    ], width=1.0, d=1.0)
    add_chamfered(get_net('LEFT', 15), [
        get_pad('LEFT', 15),
        (61.34, 58.00),
        (78.07, 58.00),
        get_pad('MOTOR2', 2)
    ], width=1.0, d=1.0)

    # M3:
    # TB2 Pad 12 (141.96, 61.21) -> Motor 3 Pad 1 (138.53, 53.94) (/M3_A)
    # TB2 Pad 13 (139.42, 61.21) -> Motor 3 Pad 2 (141.07, 53.94) (/M3_B)
    add_chamfered(get_net('RIGHT', 12), [
        get_pad('RIGHT', 12),
        (141.96, 57.00),
        (138.53, 57.00),
        get_pad('MOTOR3', 1)
    ], width=1.0, d=1.0)
    add_chamfered(get_net('RIGHT', 13), [
        get_pad('RIGHT', 13),
        (139.42, 58.50),
        (141.07, 58.50),
        get_pad('MOTOR3', 2)
    ], width=1.0, d=1.0)

    # M4:
    # TB2 Pad 14 (136.88, 61.21) -> Motor 4 Pad 1 (149.53, 53.94) (/M4_B)
    # TB2 Pad 15 (134.34, 61.21) -> Motor 4 Pad 2 (152.07, 53.94) (/M4_A)
    add_chamfered(get_net('RIGHT', 14), [
        get_pad('RIGHT', 14),
        (136.88, 56.00),
        (149.53, 56.00),
        get_pad('MOTOR4', 1)
    ], width=1.0, d=1.0)
    add_chamfered(get_net('RIGHT', 15), [
        get_pad('RIGHT', 15),
        (134.34, 57.50),
        (152.07, 57.50),
        get_pad('MOTOR4', 2)
    ], width=1.0, d=1.0)

    # =========================================================================
    # 2. TB6612 INTERNAL BRIDGES (South row)
    # =========================================================================
    # LEFT:
    add_chamfered("/AIN1_L", [get_pad('LEFT', 3), (71.50, 71.0), (66.42, 71.0), get_pad('LEFT', 5)], width=1.0, d=1.0)
    add_chamfered("/AIN2_L", [get_pad('LEFT', 2), (74.04, 68.5), (63.88, 68.5), get_pad('LEFT', 6)], width=1.0, d=1.0)
    add_chamfered("/PWMA_L", [get_pad('LEFT', 1), (76.58, 66.0), (61.34, 66.0), get_pad('LEFT', 7)], width=1.0, d=1.0)
    # Ground internal
    add_raw("GND", [get_pad('LEFT', 8), get_pad('LEFT', 16)], width=1.4)

    # RIGHT:
    add_chamfered("/AIN1_R", [get_pad('RIGHT', 5), (139.42, 71.0), (144.50, 71.0), get_pad('RIGHT', 3)], width=1.0, d=1.0)
    add_chamfered("/AIN2_R", [get_pad('RIGHT', 6), (136.88, 68.5), (147.04, 68.5), get_pad('RIGHT', 2)], width=1.0, d=1.0)
    add_chamfered("/PWMA_R", [get_pad('RIGHT', 7), (134.34, 66.0), (149.58, 66.0), get_pad('RIGHT', 1)], width=1.0, d=1.0)
    add_raw("GND", [get_pad('RIGHT', 8), get_pad('RIGHT', 16)], width=1.4)

    # =========================================================================
    # 3. TB6612 RIGHT CONTROL TO PI 4 (100% PLANAR, 0 JUMPER)
    # =========================================================================
    # STBY_R: TB2 Pad 4 (141.96) -> Pi 4 Pin 11 (114.62)
    add_chamfered("/STBY_R", [get_pad('RIGHT', 4), (141.96, 80.0), (114.62, 80.0), get_pad('Rasp_PI4', 11)], width=1.0, d=1.5)
    # AIN1_R: TB2 Pad 3 (144.50) -> Pi 4 Pin 7 (119.70)
    add_chamfered("/AIN1_R", [get_pad('RIGHT', 3), (144.50, 83.0), (119.70, 83.0), get_pad('Rasp_PI4', 7)], width=1.0, d=1.5)
    # AIN2_R: TB2 Pad 2 (147.04) -> Pi 4 Pin 5 (122.24)
    add_chamfered("/AIN2_R", [get_pad('RIGHT', 2), (147.04, 86.0), (122.24, 86.0), get_pad('Rasp_PI4', 5)], width=1.0, d=1.5)
    # PWMA_R: TB2 Pad 1 (149.58) -> Pi 4 Pin 3 (124.78)
    add_chamfered("/PWMA_R", [get_pad('RIGHT', 1), (149.58, 89.0), (124.78, 89.0), get_pad('Rasp_PI4', 3)], width=1.0, d=1.5)

    # =========================================================================
    # 4. TB6612 LEFT CONTROL TO PI 4 (2 Jumpers, 2 Planar)
    # =========================================================================
    # PWMA_L: Pad 1 (76.58) -> Pi 4 Pin 37 (81.60)
    add_chamfered("/PWMA_L", [get_pad('LEFT', 1), (76.58, 86.0), (81.60, 90.0), get_pad('Rasp_PI4', 37)], width=1.0, d=1.5)
    # STBY_L: Pad 4 (68.96) -> loops south around Pin 39/40 to Pin 38 (81.60, 96.10)
    add_chamfered("/STBY_L", [get_pad('LEFT', 4), (68.96, 98.50), (81.60, 98.50), get_pad('Rasp_PI4', 38)], width=1.0, d=1.5)

    # 2 Short Jumpers for AIN1_L & AIN2_L:
    # AIN2_L: TB1 Pad 2 (74.04) to Pi 4 Pin 35 (84.14)
    add_raw("/AIN2_L", [get_pad('LEFT', 2), (74.04, 80.00)], width=1.0)
    add_raw("/AIN2_L", [(84.14, 88.00), get_pad('Rasp_PI4', 35)], width=1.0)
    add_jumper("J_IN2_L", "/AIN2_L", (74.04, 80.00), (84.14, 88.00))

    # AIN1_L: TB1 Pad 3 (71.50) to Pi 4 Pin 33 (86.68)
    add_raw("/AIN1_L", [get_pad('LEFT', 3), (71.50, 80.00)], width=1.0)
    add_raw("/AIN1_L", [(86.68, 86.00), get_pad('Rasp_PI4', 33)], width=1.0)
    add_jumper("J_IN1_L", "/AIN1_L", (71.50, 80.00), (86.68, 86.00))

    # =========================================================================
    # 5. TCRT5000 SENSORS (100% Planar, straight vertical)
    # =========================================================================
    add_raw("/LINE_R", [get_pad('TCRT5000', 5), get_pad('Rasp_PI4', 23)], width=1.0)
    add_raw("/LINE_C", [get_pad('TCRT5000', 4), get_pad('Rasp_PI4', 21)], width=1.0)
    add_raw("/LINE_L", [get_pad('TCRT5000', 3), get_pad('Rasp_PI4', 19)], width=1.0)
    add_raw("/+3V3_LOGIC", [get_pad('TCRT5000', 2), get_pad('Rasp_PI4', 17)], width=1.0)

    # =========================================================================
    # 6. ULTRASONIC SENSORS (100% Planar, 0 Jumper)
    # =========================================================================
    # US1 Left:
    # TRIG_L: Pad 2 (88.92, 50.44) -> Pin 31 (89.22, 93.56)
    add_chamfered("/TRIG_L", [get_pad('HC_SR04_1', 2), (87.50, 52.0), (87.50, 91.0), get_pad('Rasp_PI4', 31)], width=1.0, d=1.5)
    # ECHO_L:
    add_chamfered("Net-(U_US1-ECHO)", [get_pad('HC_SR04_1', 3), (91.46, 62.0), (89.22, 62.0), get_pad('R1', 1)], width=1.0, d=1.0)
    add_raw("/ECHO_L", [get_pad('R1', 2), (96.84, 69.0), get_pad('R2', 1)], width=1.0)
    add_chamfered("/ECHO_L", [get_pad('R2', 1), (96.80, 77.0), (91.76, 77.0), get_pad('Rasp_PI4', 29)], width=1.0, d=1.5)

    # US2 Right:
    # TRIG_R: Pad 2 (117.15, 50.51) -> Pin 15 (109.54, 93.56)
    add_chamfered("/TRIG_R", [get_pad('HC_SR04_2', 2), (117.15, 53.5), (109.54, 53.5), get_pad('Rasp_PI4', 15)], width=1.0, d=1.5)
    # ECHO_R:
    add_chamfered("Net-(U_US2-ECHO)", [get_pad('HC_SR04_2', 3), (119.69, 54.0), (124.74, 54.0), get_pad('R3', 1)], width=1.0, d=1.0)
    add_raw("/ECHO_R", [get_pad('R3', 2), get_pad('R4', 1)], width=1.0)
    add_chamfered("/ECHO_R", [get_pad('R4', 1), (117.16, 70.0), (112.08, 70.0), get_pad('Rasp_PI4', 13)], width=1.0, d=1.5)

    # =========================================================================
    # 7. GROUND (GND) TRUNKS & CONNECTIONS (100% Planar, 0 Jumper)
    # =========================================================================
    # Top Ground connecting sensors:
    add_chamfered("GND", [get_pad('R2', 2), (89.18, 74.0), (94.00, 74.0), get_pad('HC_SR04_1', 4)], width=1.4, d=1.0)
    add_chamfered("GND", [get_pad('HC_SR04_1', 4), (94.00, 46.5), (109.54, 46.5), get_pad('TCRT5000', 1)], width=1.4, d=1.5)
    add_chamfered("GND", [get_pad('TCRT5000', 1), (109.54, 46.5), (122.23, 46.5), get_pad('HC_SR04_2', 4)], width=1.4, d=1.5)
    add_chamfered("GND", [get_pad('HC_SR04_2', 4), (124.78, 50.51), get_pad('R4', 2)], width=1.4, d=1.0)
    add_chamfered("GND", [get_pad('R4', 2), (124.78, 72.0), (131.80, 72.0), get_pad('RIGHT', 8)], width=1.4, d=1.0)

    # Bottom GND Trunk along Y = 101.50 (stops at X = 122.24 before +5V pin 2/4 drop!)
    trunk_gnd_y = 101.50
    add_chamfered("GND", [get_pad('LEFT', 8), (58.80, trunk_gnd_y), (77.00, trunk_gnd_y), (77.00, 93.56), get_pad('Rasp_PI4', 39)], width=1.4, d=1.5)
    add_raw("GND", [get_pad('Rasp_PI4', 40), (79.06, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 34), (86.68, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 30), (91.76, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 25), (96.84, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 20), (104.46, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 14), (112.08, trunk_gnd_y)], width=1.4)
    add_raw("GND", [get_pad('Rasp_PI4', 6), (122.24, trunk_gnd_y)], width=1.4)

    # OLED GND from TB2 Pad 8:
    add_chamfered("GND", [get_pad('RIGHT', 8), (131.80, 74.0), (149.58, 74.0), get_pad('OLED', 2)], width=1.4, d=1.5)

    # =========================================================================
    # 8. POWER (+5V_PWR & VM_MOTOR) (100% Planar, 0 Jumper)
    # =========================================================================
    # +5V Bus: Runs south of GND trunk at Y = 105.00, wraps around West (X=51.0) to North (Y=44.0)
    bus_5v_y = 105.00
    west_5v_x = 51.00
    top_5v_y = 44.00
    add_raw("/+5V_PWR", [get_pad('Rasp_PI4', 4), get_pad('Rasp_PI4', 2)], width=1.4)
    add_chamfered("/+5V_PWR", [
        get_pad('Rasp_PI4', 2),
        (127.32, bus_5v_y),
        (west_5v_x, bus_5v_y),
        (west_5v_x, top_5v_y),
        (147.04, top_5v_y),
        get_pad('RIGHT', 10)
    ], width=1.4, d=2.0)
    add_chamfered("/+5V_PWR", [(74.04, top_5v_y), get_pad('LEFT', 10)], width=1.4, d=1.0)
    add_chamfered("/+5V_PWR", [(86.38, top_5v_y), get_pad('HC_SR04_1', 1)], width=1.4, d=1.0)
    add_chamfered("/+5V_PWR", [(114.61, top_5v_y), get_pad('HC_SR04_2', 1)], width=1.4, d=1.0)

    # VM Bus: Runs at top Y = 41.50
    top_vm_y = 41.50
    add_chamfered("/VM_MOTOR", [
        get_pad('LEFT', 9),
        (76.58, top_vm_y),
        (149.58, top_vm_y),
        get_pad('RIGHT', 9)
    ], width=1.4, d=1.5)

    # =========================================================================
    # 9. OLED DISPLAY (3 JUMPERS)
    # =========================================================================
    # SDA: Pi 4 Pin 27 (94.30) to OLED Pad 4 (144.50)
    add_raw("/I2C_SDA", [get_pad('Rasp_PI4', 27), (94.30, 87.00)], width=1.0)
    add_raw("/I2C_SDA", [(144.50, 94.00), get_pad('OLED', 4)], width=1.0)
    add_jumper("J_SDA", "/I2C_SDA", (94.30, 87.00), (144.50, 94.00))

    # SCL: Pi 4 Pin 28 (94.30) to OLED Pad 3 (147.04)
    add_raw("/I2C_SCL", [get_pad('Rasp_PI4', 28), (94.30, 99.00)], width=1.0)
    add_raw("/I2C_SCL", [(147.04, 99.00), get_pad('OLED', 3)], width=1.0)
    add_jumper("J_SCL", "/I2C_SCL", (94.30, 99.00), (147.04, 99.00))

    # +3V3: Pi 4 Pin 17 (107.00) to OLED Pad 1 (152.12)
    add_raw("/+3V3_LOGIC", [get_pad('Rasp_PI4', 17), (107.00, 84.00)], width=1.0)
    add_raw("/+3V3_LOGIC", [(152.12, 94.00), get_pad('OLED', 1)], width=1.0)
    add_jumper("J_3V3", "/+3V3_LOGIC", (107.00, 84.00), (152.12, 94.00))

route_all()

print(f"Total track segments routed: {len(paths)}")
print(f"Total jumpers required: {len(jumpers)} (total {len(jumpers)*2} vias)")

# Verify conflicts between tracks
conflicts = []
for i in range(len(paths)):
    for j in range(i + 1, len(paths)):
        if paths[i]['net'] == paths[j]['net']: continue
        d = seg_seg_dist(paths[i]['p1'], paths[i]['p2'], paths[j]['p1'], paths[j]['p2'])
        req = (paths[i]['width'] + paths[j]['width']) / 2.0 + 0.45 # 0.45mm clearance
        if d < req:
            conflicts.append((paths[i], paths[j], d, req))

print(f"\nTrack-to-Track Conflicts found: {len(conflicts)}")
for p1, p2, d, req in conflicts[:20]:
    print(f"  CONFLICT: {p1['net']} ({p1['p1']}->{p1['p2']}) vs {p2['net']} ({p2['p1']}->{p2['p2']}): dist={d:.3f} < req={req:.3f}")
