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

paths = []
def add_chamfered(net, pts, width=1.0, d=1.5):
    c_pts = chamfer_path(pts, d=d)
    for i in range(len(c_pts) - 1):
        paths.append({'net': net, 'p1': c_pts[i], 'p2': c_pts[i+1], 'width': width})

m1 = {1: (66.41, 53.40), 2: (68.95, 53.40)}
m2 = {1: (75.53, 53.44), 2: (78.07, 53.44)}
m3 = {1: (138.53, 53.94), 2: (141.07, 53.94)}
m4 = {1: (149.53, 53.94), 2: (152.07, 53.94)}

tb1_n = {
    12: (68.96, 61.21), 13: (66.42, 61.21), 14: (63.88, 61.21), 15: (61.34, 61.21)
}
tb2_n = {
    12: (141.96, 61.21), 13: (139.42, 61.21), 14: (136.88, 61.21), 15: (134.34, 61.21)
}

# Left Motors:
# M1 (from Channel B 14, 15):
add_chamfered("/M1_B", [tb1_n[14], (63.88, 57.0), (68.95, 57.0), m1[2]], width=1.0, d=1.0)
add_chamfered("/M1_A", [tb1_n[15], (61.34, 58.5), (66.41, 58.5), m1[1]], width=1.0, d=1.0)
# M2 (from Channel A 12, 13):
add_chamfered("/M2_B", [tb1_n[13], (66.42, 57.0), (75.53, 57.0), m2[1]], width=1.0, d=1.0)
add_chamfered("/M2_A", [tb1_n[12], (68.96, 58.5), (78.07, 58.5), m2[2]], width=1.0, d=1.0)

# Right Motors:
# M3 (from Channel B 14, 15):
add_chamfered("/M3_B", [tb2_n[14], (136.88, 57.0), (141.07, 57.0), m3[2]], width=1.0, d=1.0)
add_chamfered("/M3_A", [tb2_n[15], (134.34, 58.5), (138.53, 58.5), m3[1]], width=1.0, d=1.0)
# M4 (from Channel A 12, 13):
add_chamfered("/M4_B", [tb2_n[13], (139.42, 57.0), (149.53, 57.0), m4[1]], width=1.0, d=1.0)
add_chamfered("/M4_A", [tb2_n[12], (141.96, 58.5), (152.07, 58.5), m4[2]], width=1.0, d=1.0)

conflicts = []
for i in range(len(paths)):
    for j in range(i + 1, len(paths)):
        if paths[i]['net'] == paths[j]['net']: continue
        d = chk.seg_seg_dist(paths[i]['p1'], paths[i]['p2'], paths[j]['p1'], paths[j]['p2'])
        req = (paths[i]['width'] + paths[j]['width']) / 2.0 + 0.45
        if d < req:
            conflicts.append((paths[i], paths[j], d))

print(f"Total motor path segments: {len(paths)}")
print(f"Motor conflicts found: {len(conflicts)}")
for p1, p2, d in conflicts:
    print(f"CONFLICT: {p1['net']} and {p2['net']}, dist={d}")
