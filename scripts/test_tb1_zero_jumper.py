import math
import check_v21_conflicts as chk

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
        dot = ux1 * ux2 + uy1 * ux2
        if abs(dot) < 0.25:
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

# TB1:
# North row (Y = 61.21):
# (58.80): VM, (61.34): +5V, (63.88): GND, (66.42): M1_A, (68.96): M1_B, (71.50): M2_B, (74.04): M2_A, (76.58): GND
# South row (Y = 76.45):
# (58.80): PWMA, (61.34): AIN2, (63.88): AIN1, (66.42): STBY, (68.96): BIN1, (71.50): BIN2, (74.04): PWMB, (76.58): GND

# M1 and M2:
m1_1 = (66.41, 53.40) # M1_A
m1_2 = (68.95, 53.40) # M1_B
m2_1 = (75.53, 53.44) # M2_B
m2_2 = (78.07, 53.44) # M2_A

add_chamfered("/M1_A", [(66.42, 61.21), m1_1], width=1.0, d=1.0)
add_chamfered("/M1_B", [(68.96, 61.21), m1_2], width=1.0, d=1.0)
add_chamfered("/M2_B", [(71.50, 61.21), (71.50, 56.0), (75.53, 56.0), m2_1], width=1.0, d=1.0)
add_chamfered("/M2_A", [(74.04, 61.21), (74.04, 57.5), (78.07, 57.5), m2_2], width=1.0, d=1.0)

# South control to Pi 4:
pi_pwma_l = (81.60, 93.5575) # Pin 37
pi_ain2_l = (84.14, 93.5575) # Pin 35
pi_ain1_l = (86.68, 93.5575) # Pin 33
pi_stby_l = (81.60, 96.0975) # Pin 38

add_chamfered("/PWMA_L", [(74.04, 76.45), (74.04, 83.0), (81.60, 83.0), pi_pwma_l], width=1.0, d=1.5)
add_chamfered("/AIN2_L", [(71.50, 76.45), (71.50, 85.5), (84.14, 85.5), pi_ain2_l], width=1.0, d=1.5)
add_chamfered("/AIN1_L", [(68.96, 76.45), (68.96, 88.0), (86.68, 88.0), pi_ain1_l], width=1.0, d=1.5)
add_chamfered("/STBY_L", [(66.42, 76.45), (66.42, 98.5), (81.60, 98.5), pi_stby_l], width=1.0, d=1.5)

conflicts = []
for i in range(len(paths)):
    for j in range(i + 1, len(paths)):
        if paths[i]['net'] == paths[j]['net']: continue
        d = chk.seg_seg_dist(paths[i]['p1'], paths[i]['p2'], paths[j]['p1'], paths[j]['p2'])
        req = (paths[i]['width'] + paths[j]['width']) / 2.0 + 0.45
        if d < req:
            conflicts.append((paths[i], paths[j], d))

print(f"Total TB1 path segments: {len(paths)}")
print(f"Conflicts found: {len(conflicts)}")
for p1, p2, d in conflicts:
    print(f"CONFLICT: {p1['net']} and {p2['net']}, dist={d}")

