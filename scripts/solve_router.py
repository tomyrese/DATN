import math
import re

content = open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8').read()
net_ids = {}
for m in re.finditer(r'\(net\s+(\d+)\s+"([^"]*)"\)', content):
    net_ids[m.group(2)] = int(m.group(1))

pads = {}
fp_indices = [m.start() for m in re.finditer(r'\(footprint\s+"', content)]
fp_indices.append(len(content))
for i in range(len(fp_indices) - 1):
    fp_str = content[fp_indices[i]:fp_indices[i+1]]
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', fp_str)
    ref = ref_m.group(1) if ref_m else '?'
    at_m = re.search(r'\(at\s+([0-9.-]+)\s+([0-9.-]+)(?:\s+([0-9.-]+))?\)', fp_str)
    fcx = float(at_m.group(1)) if at_m else 0.0
    fcy = float(at_m.group(2)) if at_m else 0.0
    frot = float(at_m.group(3)) if at_m and at_m.group(3) else 0.0
    rad = math.radians(frot)
    pad_matches = re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([0-9.-]+)\s+([0-9.-]+)[^\)]*\)(.*?)(?=\n\t\t\(pad|\n\t\))', fp_str, re.DOTALL)
    for pm in pad_matches:
        pnum = pm.group(1)
        px_rel = float(pm.group(2))
        py_rel = float(pm.group(3))
        prest = pm.group(4)
        net_m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]+)"\)', prest)
        nname = net_m.group(1) if net_m else "None"
        rx = px_rel * math.cos(rad) - py_rel * math.sin(rad)
        ry = px_rel * math.sin(rad) + py_rel * math.cos(rad)
        abs_x = round(fcx + rx, 2)
        abs_y = round(fcy + ry, 2)
        pads[(ref, pnum)] = (abs_x, abs_y, nname)

tracks = []

def dist_pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx*dx + dy*dy
    if l2 < 1e-6:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1)*dx + (py - y1)*dy) / l2))
    return math.hypot(px - (x1 + t*dx), py - (y1 + t*dy))

def dist_seg_seg(x1, y1, x2, y2, x3, y3, x4, y4):
    min_d = 999.0
    for s in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        sx = x1 + s*(x2 - x1)
        sy = y1 + s*(y2 - y1)
        min_d = min(min_d, dist_pt_seg(sx, sy, x3, y3, x4, y4))
    for s in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        sx = x3 + s*(x4 - x3)
        sy = y3 + s*(y4 - y3)
        min_d = min(min_d, dist_pt_seg(sx, sy, x1, y1, x2, y2))
    return min_d

def chamfer_polyline(points, d=1.0):
    if len(points) < 2: return []
    if len(points) == 2:
        p1, p2 = points[0], points[1]
        if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) > 1e-3:
            return [(p1, p2)]
        return []

    new_pts = [points[0]]
    for i in range(1, len(points) - 1):
        prev_p = points[i - 1]
        curr_p = points[i]
        next_p = points[i + 1]

        v1 = (curr_p[0] - prev_p[0], curr_p[1] - prev_p[1])
        v2 = (next_p[0] - curr_p[0], next_p[1] - curr_p[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        if l1 < 1e-4 or l2 < 1e-4: continue

        u1 = (v1[0] / l1, v1[1] / l1)
        u2 = (v2[0] / l2, v2[1] / l2)
        dot = max(-1.0, min(1.0, u1[0]*u2[0] + u1[1]*u2[1]))
        angle = math.degrees(math.acos(dot))

        if abs(angle - 90.0) < 5.0:
            actual_d = min(d, l1 * 0.45, l2 * 0.45)
            p_in = (round(curr_p[0] - u1[0] * actual_d, 2), round(curr_p[1] - u1[1] * actual_d, 2))
            p_out = (round(curr_p[0] + u2[0] * actual_d, 2), round(curr_p[1] + u2[1] * actual_d, 2))
            new_pts.append(p_in)
            new_pts.append(p_out)
        else:
            new_pts.append(curr_p)

    new_pts.append(points[-1])
    segs = []
    for k in range(len(new_pts) - 1):
        pt1, pt2 = new_pts[k], new_pts[k+1]
        if math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1]) > 1e-3:
            segs.append((pt1, pt2))
    return segs

def add_route(net_name, points, width=1.0):
    nid = net_ids.get(net_name, 0)
    segs = chamfer_polyline(points)
    for (p1, p2) in segs:
        tracks.append((p1[0], p1[1], p2[0], p2[1], width, net_name, nid))

# 1. Left Motor Control
add_route("DRV_L_PWMA", [pads[('J_PI_IDC40', '19')][:2], pads[('U_DRV_L_CTL', '1')][:2]], width=1.0)
add_route("DRV_L_AIN2", [pads[('J_PI_IDC40', '21')][:2], pads[('U_DRV_L_CTL', '2')][:2]], width=1.0)
add_route("DRV_L_AIN1", [pads[('J_PI_IDC40', '23')][:2], pads[('U_DRV_L_CTL', '3')][:2]], width=1.0)
add_route("DRV_L_STBY", [(26.16, 36.48), pads[('U_DRV_L_CTL', '4')][:2]], width=1.0) # only to STBY pin
add_route("DRV_L_BIN1", [pads[('J_PI_IDC40', '29')][:2], (32.40, 41.56), (30.00, 39.02), pads[('U_DRV_L_CTL', '5')][:2]], width=1.0)
add_route("DRV_L_BIN2", [pads[('J_PI_IDC40', '31')][:2], (32.40, 44.10), (30.00, 41.56), pads[('U_DRV_L_CTL', '6')][:2]], width=1.0)
add_route("DRV_L_PWMB", [pads[('J_PI_IDC40', '33')][:2], (32.40, 46.64), (30.00, 44.10), pads[('U_DRV_L_CTL', '7')][:2]], width=1.0)

# 2. Right Motor Control
add_route("DRV_R_PWMA", [pads[('J_PI_IDC40', '16')][:2], pads[('U_DRV_R_CTL', '1')][:2]], width=1.0)
add_route("DRV_R_AIN2", [pads[('J_PI_IDC40', '18')][:2], pads[('U_DRV_R_CTL', '2')][:2]], width=1.0)
add_route("DRV_R_AIN1", [pads[('J_PI_IDC40', '22')][:2], (52.68, 31.40), (55.00, 28.86), pads[('U_DRV_R_CTL', '3')][:2]], width=1.0)
add_route("DRV_R_STBY", [pads[('U_DRV_R_CTL', '4')][:2], pads[('R_STBY_R', '1')][:2]], width=1.0)
add_route("DRV_R_BIN1", [pads[('J_PI_IDC40', '24')][:2], pads[('U_DRV_R_CTL', '5')][:2]], width=1.0)
add_route("DRV_R_BIN2", [pads[('J_PI_IDC40', '26')][:2], pads[('U_DRV_R_CTL', '6')][:2]], width=1.0)
add_route("DRV_R_PWMB", [pads[('J_PI_IDC40', '32')][:2], (50.14, 44.10), (53.00, 44.10), (55.00, 39.02), pads[('U_DRV_R_CTL', '7')][:2]], width=1.0)

# 3. Left Motor Outputs
add_route("DRV_L_AO1", [pads[('U_DRV_L_PWR', '4')][:2], pads[('J_MOT_L', '1')][:2]], width=1.0)
add_route("DRV_L_AO2", [pads[('U_DRV_L_PWR', '5')][:2], pads[('J_MOT_L', '2')][:2]], width=1.0)
add_route("DRV_L_BO2", [pads[('U_DRV_L_PWR', '6')][:2], pads[('J_MOT_L', '3')][:2]], width=1.0)
add_route("DRV_L_BO1", [pads[('U_DRV_L_PWR', '7')][:2], pads[('J_MOT_L', '4')][:2]], width=1.0)

# 4. Right Motor Outputs
add_route("DRV_R_AO1", [pads[('U_DRV_R_PWR', '4')][:2], pads[('J_MOT_R', '1')][:2]], width=1.0)
add_route("DRV_R_AO2", [pads[('U_DRV_R_PWR', '5')][:2], pads[('J_MOT_R', '2')][:2]], width=1.0)
add_route("DRV_R_BO2", [pads[('U_DRV_R_PWR', '6')][:2], pads[('J_MOT_R', '3')][:2]], width=1.0)
add_route("DRV_R_BO1", [pads[('U_DRV_R_PWR', '7')][:2], pads[('J_MOT_R', '4')][:2]], width=1.0)

# 5. OLED I2C & Jump
add_route("I2C_SDA", [pads[('J_PI_IDC40', '3')][:2], pads[('R_JMP1', '2')][:2]], width=1.0)
add_route("I2C_SDA", [pads[('R_JMP1', '1')][:2], (21.50, 8.54), (19.50, 7.50), pads[('J_OLED', '4')][:2]], width=1.0)
add_route("I2C_SCL", [pads[('J_PI_IDC40', '5')][:2], (30.00, 11.08), (28.00, 9.08), (28.00, 8.00), (17.00, 8.00), pads[('J_OLED', '3')][:2]], width=1.0)

# 6. Sonar L
add_route("SONAR_L_TRIG", [pads[('J_PI_IDC40', '7')][:2], (39.50, 12.00), (8.50, 12.00), pads[('J_SONAR_L', '2')][:2]], width=1.0)
add_route("SONAR_L_ECHO_5V", [pads[('J_SONAR_L', '3')][:2], (11.00, 16.00), (17.00, 16.00), pads[('R_ECHOL_1', '1')][:2]], width=1.0)
add_route("SONAR_L_ECHO_3V3", [pads[('R_ECHOL_1', '2')][:2], pads[('R_ECHOL_2', '1')][:2]], width=1.0)
add_route("SONAR_L_ECHO_3V3", [pads[('R_ECHOL_2', '1')][:2], (35.00, 18.70), (36.50, 17.20), (39.50, 17.20), pads[('J_PI_IDC40', '11')][:2]], width=1.0)

# 7. Sonar R
add_route("SONAR_R_TRIG", [pads[('J_PI_IDC40', '13')][:2], (39.50, 20.00), (8.50, 20.00), pads[('J_SONAR_R', '2')][:2]], width=1.0)
add_route("SONAR_R_ECHO_5V", [pads[('J_SONAR_R', '3')][:2], (11.00, 23.78), pads[('R_ECHOR_1', '1')][:2]], width=1.0)
add_route("SONAR_R_ECHO_3V3", [pads[('R_ECHOR_1', '2')][:2], pads[('R_ECHOR_2', '1')][:2]], width=1.0)
add_route("SONAR_R_ECHO_3V3", [pads[('R_ECHOR_2', '1')][:2], (35.00, 23.78), (36.50, 22.28), (39.50, 22.28), pads[('J_PI_IDC40', '15')][:2]], width=1.0)

# 8. 12V_BAT (1.5mm)
# South perimeter bus Y = 62.50
add_route("12V_BAT", [pads[('J_BAT', '1')][:2], (10.00, 62.50), (33.00, 62.50), pads[('U_BUCK', '1')][:2]], width=1.5)
# Left VM: from J_BAT.1 (10.00, 58.00) goes along West margin X=2.00 up to Y=28.86 into U_DRV_L_PWR.1 (12.00, 28.86)
add_route("12V_BAT", [pads[('J_BAT', '1')][:2], (5.00, 58.00), (2.00, 55.00), (2.00, 28.86), pads[('U_DRV_L_PWR', '1')][:2]], width=1.5)
# Right VM: from South bus goes up channel at X=64.00 under R_STBY_R (31.40) to U_DRV_R_PWR.1 (73.00, 23.78)
add_route("12V_BAT", [(33.00, 62.50), (64.00, 62.50), (64.00, 23.78), pads[('U_DRV_R_PWR', '1')][:2]], width=1.5)

# 9. 5V_BUCK (1.5mm)
# Feeder: U_BUCK.3 (27.92, 58.00) up to Y=55.50, east to J_PWR_PI.1 (55.00, 58.00)
add_route("5V_BUCK", [pads[('U_BUCK', '3')][:2], (27.92, 55.50), (55.00, 55.50), pads[('J_PWR_PI', '1')][:2]], width=1.5)
# East margin highway at X=83.50 up to North bus at Y=1.20, down West margin at X=2.00 to J_SONAR_L.1 & J_SONAR_R.1
add_route("5V_BUCK", [(55.00, 55.50), (83.50, 55.50), (83.50, 1.20), (2.00, 1.20), (2.00, 13.62), pads[('J_SONAR_L', '1')][:2]], width=1.5)
add_route("5V_BUCK", [(2.00, 13.62), (2.00, 21.24), pads[('J_SONAR_R', '1')][:2]], width=1.5)

# 10. 3V3 (1.5mm)
# North bus at Y = 3.20: IDC40.1 (41.23, 6.00) -> (41.23, 3.20) -> (12.00, 3.20) -> J_OLED.1 (12.00, 6.00)
add_route("3V3", [pads[('J_PI_IDC40', '1')][:2], (41.23, 3.20), (12.00, 3.20), pads[('J_OLED', '1')][:2]], width=1.5)
# Right Driver & STBY_R: along North bus to X=68.50, drops down to U_DRV_R_PWR.2 (73.00, 26.32) and R_STBY_R.2 (71.16, 31.40)
add_route("3V3", [(41.23, 3.20), (68.50, 3.20), (68.50, 26.32), pads[('U_DRV_R_PWR', '2')][:2]], width=1.5)
add_route("3V3", [(68.50, 26.32), (68.50, 31.40), pads[('R_STBY_R', '2')][:2]], width=1.5)
# Left Driver & STBY_L: drops down through X=25.00 to U_DRV_L_PWR.2 (12.00, 31.40) and R_STBY_L.2 (26.16, 36.48)
add_route("3V3", [(12.00, 3.20), (14.50, 3.20), (14.50, 31.40), pads[('U_DRV_L_PWR', '2')][:2]], width=1.5)
add_route("3V3", [pads[('U_DRV_L_PWR', '2')][:2], (14.50, 31.40), (14.50, 36.48), pads[('R_STBY_L', '2')][:2]], width=1.5)

# 11. GND (1.5mm)
# South ground bus along Y = 60.00
add_route("GND", [pads[('J_BAT', '2')][:2], (15.08, 60.00), (25.38, 60.00), pads[('U_BUCK', '4')][:2]], width=1.5)
add_route("GND", [(25.38, 60.00), (30.46, 60.00), pads[('U_BUCK', '2')][:2]], width=1.5)
add_route("GND", [(30.46, 60.00), (41.23, 60.00), pads[('J_PI_IDC40', '39')][:2]], width=1.5)
add_route("GND", [(41.23, 60.00), (55.00, 60.00), pads[('J_PWR_PI', '2')][:2]], width=1.5)
# North GND bus at Y = 5.00: IDC40.6 (43.77, 11.08) -> (45.00, 11.08) -> (45.00, 5.00) -> (14.50, 5.00) -> J_OLED.2 (14.50, 6.00)
add_route("GND", [pads[('J_PI_IDC40', '6')][:2], (45.00, 11.08), (45.00, 5.00), (14.50, 5.00), pads[('J_OLED', '2')][:2]], width=1.5)
# Connect Sonar sensor GNDs (13.50, 13.62) & (13.50, 21.24):
add_route("GND", [pads[('J_SONAR_L', '4')][:2], pads[('J_SONAR_R', '4')][:2]], width=1.5)
# Connect Resistor divider GNDs at X=38.16 to IDC40.6:
add_route("GND", [pads[('R_ECHOL_2', '2')][:2], pads[('R_ECHOR_2', '2')][:2]], width=1.5)
add_route("GND", [pads[('R_ECHOL_2', '2')][:2], (38.16, 15.00), (43.77, 15.00), pads[('J_PI_IDC40', '6')][:2]], width=1.5)
# Right Driver GND:
add_route("GND", [pads[('J_PI_IDC40', '34')][:2], (52.00, 46.64), (55.00, 41.56), pads[('U_DRV_R_CTL', '8')][:2]], width=1.5)
add_route("GND", [pads[('U_DRV_R_CTL', '8')][:2], pads[('U_DRV_R_PWR', '8')][:2]], width=1.5)
add_route("GND", [pads[('U_DRV_R_PWR', '8')][:2], (71.00, 41.56), (71.00, 28.86), pads[('U_DRV_R_PWR', '3')][:2]], width=1.5)
# Left Driver GND:
add_route("GND", [pads[('J_PI_IDC40', '39')][:2], (37.00, 54.26), (27.00, 48.00), pads[('U_DRV_L_CTL', '8')][:2]], width=1.5)
add_route("GND", [pads[('U_DRV_L_CTL', '8')][:2], (25.38, 46.64), pads[('U_DRV_L_PWR', '8')][:2]], width=1.5)
# Connect Left Driver GND to South GND:
add_route("GND", [pads[('U_DRV_L_PWR', '8')][:2], (12.00, 52.00), (15.08, 55.00), pads[('J_BAT', '2')][:2]], width=1.5)
# Connect Left Driver U_DRV_L_PWR.3 (GND) to J_SONAR_R.4 (GND):
add_route("GND", [pads[('J_SONAR_R', '4')][:2], (13.50, 33.94), pads[('U_DRV_L_PWR', '3')][:2]], width=1.5)

print(f"Total track segments: {len(tracks)}")

# Check collisions
collisions = []
for i in range(len(tracks)):
    x1, y1, x2, y2, w1, n1, nid1 = tracks[i]
    for j in range(i + 1, len(tracks)):
        x3, y3, x4, y4, w2, n2, nid2 = tracks[j]
        if n1 == n2: continue

        d = dist_seg_seg(x1, y1, x2, y2, x3, y3, x4, y4)
        req = (w1 + w2)/2.0 + 0.35 # clearance
        if d < req:
            collisions.append((n1, n2, (x1, y1, x2, y2), (x3, y3, x4, y4), d, w1, w2))

print(f"Total copper collisions: {len(collisions)}")
for c in collisions:
    print(f"COLLISION: {c[0]} with {c[1]} dist={c[4]:.2f}")
    print(f"   Seg 1: {c[2]} w={c[5]}")
    print(f"   Seg 2: {c[3]} w={c[6]}")
