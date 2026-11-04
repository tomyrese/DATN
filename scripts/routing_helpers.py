import math
from init_world_pads import world_pads, net_id

def pad(ref, p_num):
    p = world_pads[ref][str(p_num)]
    return (p['x'], p['y'])

def chamfer_path(pts, d=1.2):
    if len(pts) <= 2: return list(pts)
    result = [pts[0]]
    for i in range(1, len(pts) - 1):
        p_prev, p_curr, p_next = pts[i - 1], pts[i], pts[i + 1]
        dx1, dy1 = p_curr[0] - p_prev[0], p_curr[1] - p_prev[1]
        len1 = math.hypot(dx1, dy1)
        dx2, dy2 = p_next[0] - p_prev[0], p_next[1] - p_curr[1] # wait, p_next - p_curr!
        len2 = math.hypot(p_next[0] - p_curr[0], p_next[1] - p_curr[1])
        if len1 < 1e-4 or len2 < 1e-4: continue
        dx2, dy2 = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
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
    for i in range(len(c_pts) - 1):
        tracks.append({
            'net': net,
            'net_id': net_id[net],
            'p1': c_pts[i],
            'p2': c_pts[i+1],
            'width': width
        })

def add_raw(net, pts, width=1.0):
    for i in range(len(pts) - 1):
        tracks.append({
            'net': net,
            'net_id': net_id[net],
            'p1': pts[i],
            'p2': pts[i+1],
            'width': width
        })

print("Routing helper initialized.")

