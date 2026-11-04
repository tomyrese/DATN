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

# Motor routing direct North from .bak:
# M1:
add_chamfered("/M1_A", [(66.42, 61.21), (66.41, 53.40)], width=1.0, d=1.0)
add_chamfered("/M1_B", [(68.96, 61.21), (68.95, 53.40)], width=1.0, d=1.0)
# M2:
add_chamfered("/M2_B", [(71.50, 61.21), (71.50, 54.24), (72.30, 53.44), (75.53, 53.44)], width=1.0, d=1.0)
add_chamfered("/M2_A", [(74.04, 61.21), (74.04, 59.70), (78.07, 55.67), (78.07, 53.44)], width=1.0, d=1.0)

# M3:
add_chamfered("/M3_A", [(139.42, 61.21), (139.42, 58.56), (138.53, 57.67), (138.53, 53.94)], width=1.0, d=1.0)
add_chamfered("/M3_B", [(141.96, 61.21), (141.96, 57.10), (141.07, 56.21), (141.07, 53.94)], width=1.0, d=1.0)
# M4:
add_chamfered("/M4_B", [(144.50, 61.21), (144.50, 55.74), (146.30, 53.94), (149.53, 53.94)], width=1.0, d=1.0)
add_chamfered("/M4_A", [(147.04, 61.21), (147.04, 58.70), (148.30, 57.44), (150.80, 57.44), (152.07, 56.17), (152.07, 53.94)], width=1.0, d=1.0)

conflicts = []
for i in range(len(paths)):
    for j in range(i + 1, len(paths)):
        if paths[i]['net'] == paths[j]['net']: continue
        d = chk.seg_seg_dist(paths[i]['p1'], paths[i]['p2'], paths[j]['p1'], paths[j]['p2'])
        req = (paths[i]['width'] + paths[j]['width']) / 2.0 + 0.45
        if d < req:
            conflicts.append((paths[i], paths[j], d))

print(f"Total direct motor path segments: {len(paths)}")
print(f"Conflicts found: {len(conflicts)}")
for p1, p2, d in conflicts:
    print(f"CONFLICT: {p1['net']} and {p2['net']}, dist={d}")

