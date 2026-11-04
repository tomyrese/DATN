import math
import check_v21_conflicts as chk

def chamfer_path(pts, d=1.0):
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
def add_chamfered(net, pts, width=1.0, d=1.0):
    c_pts = chamfer_path(pts, d=d)
    for i in range(len(c_pts) - 1):
        paths.append({'net': net, 'p1': c_pts[i], 'p2': c_pts[i+1], 'width': width})

def test_option_1():
    paths.clear()
    # M1 direct
    add_chamfered("/M1_A", [(68.96, 61.21), (68.95, 53.40)], width=1.0)
    add_chamfered("/M1_B", [(66.42, 61.21), (66.41, 53.40)], width=1.0)

    # M2 via West channel:
    # Pad 14 (63.88) -> west to 56.5 -> north to 48.5 -> east to 75.53 -> south to (75.53, 53.44)
    add_chamfered("/M2_B", [
        (63.88, 61.21),
        (63.88, 59.50),
        (56.50, 59.50),
        (56.50, 48.50),
        (75.53, 48.50),
        (75.53, 53.44)
    ], width=1.0)

    # Pad 15 (61.34) -> west to 55.0 -> north to 46.5 -> east to 78.07 -> south to (78.07, 53.44)
    add_chamfered("/M2_A", [
        (61.34, 61.21),
        (61.34, 58.00),
        (55.00, 58.00),
        (55.00, 46.50),
        (78.07, 46.50),
        (78.07, 53.44)
    ], width=1.0)

    # VM feeding TB1 Pad 9 (76.58) from East at Y = 61.21:
    # VM bus comes at Y = 41.50, drops at X = 80.00 down to Y = 61.21, then west to 76.58:
    add_chamfered("/VM_MOTOR", [
        (149.58, 41.50),
        (80.00, 41.50),
        (80.00, 61.21),
        (76.58, 61.21)
    ], width=1.4)

    # +5V feeding TB1 Pad 10 (74.04) from East:
    # drops at X = 81.50 down to Y = 62.70, then west to 74.04:
    add_chamfered("/+5V_PWR", [
        (147.04, 44.00),
        (81.50, 44.00),
        (81.50, 62.70),
        (74.04, 62.70),
        (74.04, 61.21)
    ], width=1.4)

    conflicts = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            if paths[i]['net'] == paths[j]['net']: continue
            d = chk.seg_seg_dist(paths[i]['p1'], paths[i]['p2'], paths[j]['p1'], paths[j]['p2'])
            req = (paths[i]['width'] + paths[j]['width']) / 2.0 + 0.45
            if d < req:
                conflicts.append((paths[i], paths[j], d, req))

    print(f"Option 1 Total Segments: {len(paths)}, Conflicts: {len(conflicts)}")
    for p1, p2, d, req in conflicts:
        print(f"  Conflict: {p1['net']} vs {p2['net']}, dist={d:.3f} < {req:.3f}")

test_option_1()

