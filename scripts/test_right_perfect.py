import math

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
        if abs(dot) < 0.25:
            actual_d = min(d, len1 * 0.40, len2 * 0.40)
            p_in = (round(p_curr[0] - ux1 * actual_d, 4), round(p_curr[1] - uy1 * actual_d, 4))
            p_out = (round(p_curr[0] + ux2 * actual_d, 4), round(p_curr[1] + uy2 * actual_d, 4))
            result.append(p_in); result.append(p_out)
        else:
            result.append(p_curr)
    result.append(pts[-1])
    return result

import check_v21_conflicts as chk

paths = []
def add_chamfered(net, pts, width=1.0, d=1.5):
    c_pts = chamfer_path(pts, d=d)
    for i in range(len(c_pts) - 1):
        paths.append({'net': net, 'p1': c_pts[i], 'p2': c_pts[i+1], 'width': width})

# Pad 4 (STBY_R), Pad 3 (AIN1_R), Pad 2 (AIN2_R), Pad 1 (PWMA_R)
tb2_s = {
    1: (149.58, 76.45), 2: (147.04, 76.45), 3: (144.50, 76.45), 4: (141.96, 76.45),
    5: (139.42, 76.45), 6: (136.88, 76.45), 7: (134.34, 76.45), 8: (131.80, 76.45)
}

pi_p11 = (114.62, 93.5575) # STBY_R
pi_p7  = (119.70, 93.5575) # AIN1_R
pi_p5  = (122.24, 93.5575) # AIN2_R
pi_p3  = (124.78, 93.5575) # PWMA_R

# Bridges inside TB2 between 1-7, 2-6, 3-5:
add_chamfered("/AIN1_R", [tb2_s[5], (139.42, 71.0), (144.50, 71.0), tb2_s[3]], width=1.0, d=1.0)
add_chamfered("/AIN2_R", [tb2_s[6], (136.88, 68.5), (147.04, 68.5), tb2_s[2]], width=1.0, d=1.0)
add_chamfered("/PWMA_R", [tb2_s[7], (134.34, 66.0), (149.58, 66.0), tb2_s[1]], width=1.0, d=1.0)

# 4 concentric planar lines from TB2 South row to Pi 4:
add_chamfered("/STBY_R", [tb2_s[4], (141.96, 80.0), (114.62, 80.0), pi_p11], width=1.0, d=1.5)
add_chamfered("/AIN1_R", [tb2_s[3], (144.50, 83.0), (119.70, 83.0), pi_p7], width=1.0, d=1.5)
add_chamfered("/AIN2_R", [tb2_s[2], (147.04, 86.0), (122.24, 86.0), pi_p5], width=1.0, d=1.5)
add_chamfered("/PWMA_R", [tb2_s[1], (149.58, 89.0), (124.78, 89.0), pi_p3], width=1.0, d=1.5)

conflicts = []
for i in range(len(paths)):
    for j in range(i + 1, len(paths)):
        if paths[i]['net'] == paths[j]['net']: continue
        d = chk.seg_seg_dist(paths[i]['p1'], paths[i]['p2'], paths[j]['p1'], paths[j]['p2'])
        req = (paths[i]['width'] + paths[j]['width']) / 2.0 + 0.45
        if d < req:
            conflicts.append((paths[i], paths[j], d))

print(f"Total test paths: {len(paths)}")
print(f"Conflicts found: {len(conflicts)}")
for p1, p2, d in conflicts:
    print(f"CONFLICT: {p1['net']} and {p2['net']}, dist={d}")

