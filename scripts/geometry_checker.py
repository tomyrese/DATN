import math

def seg_distance(p1, p2, p3, p4):
    # Minimum distance between segment p1-p2 and segment p3-p4
    # Line segments: s1(t) = p1 + t*(p2-p1), s2(u) = p3 + u*(p4-p3) for t, u in [0, 1]
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (p4[0] - p3[0], p4[1] - p3[1])
    r = (p1[0] - p3[0], p1[1] - p3[1])
    a = d1[0]*d1[0] + d1[1]*d1[1]
    e = d2[0]*d2[0] + d2[1]*d2[1]
    f = d2[0]*r[0] + d2[1]*r[1]

    if a <= 1e-8 and e <= 1e-8:
        return math.hypot(p1[0]-p3[0], p1[1]-p3[1])
    if a <= 1e-8:
        s = 0.0
        t = max(0.0, min(1.0, f / e))
    else:
        c = d1[0]*r[0] + d1[1]*r[1]
        if e <= 1e-8:
            t = 0.0
            s = max(0.0, min(1.0, -c / a))
        else:
            b = d1[0]*d2[0] + d1[1]*d2[1]
            denom = a*e - b*b
            if denom != 0.0:
                s = max(0.0, min(1.0, (b*f - c*e) / denom))
            else:
                s = 0.0
            t = (b*s + f) / e
            if t < 0.0:
                t = 0.0
                s = max(0.0, min(1.0, -c / a))
            elif t > 1.0:
                t = 1.0
                s = max(0.0, min(1.0, (b - c) / a))

    c1 = (p1[0] + s * d1[0], p1[1] + s * d1[1])
    c2 = (p3[0] + t * d2[0], p3[1] + t * d2[1])
    return math.hypot(c1[0]-c2[0], c1[1]-c2[1])

def point_to_seg_dist(pt, p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    l2 = dx*dx + dy*dy
    if l2 <= 1e-8:
        return math.hypot(pt[0]-p1[0], pt[1]-p1[1])
    t = max(0.0, min(1.0, ((pt[0]-p1[0])*dx + (pt[1]-p1[1])*dy) / l2))
    proj = (p1[0] + t*dx, p1[1] + t*dy)
    return math.hypot(pt[0]-proj[0], pt[1]-proj[1])

def check_clearance(tracks, world_pads, min_clearance=0.5):
    violations = []
    # 1. Track vs Pad of DIFFERENT net
    for t in tracks:
        t_net = t['net']
        t_w = t['width']
        p1, p2 = t['p1'], t['p2']
        for ref, p_dict in world_pads.items():
            for p_num, pad in p_dict.items():
                p_net = pad['net_name']
                if not p_net or p_net == t_net:
                    continue
                # Ignore unconnected pads on Pi 4
                if 'unconnected' in p_net:
                    continue
                pad_pt = (pad['x'], pad['y'])
                pad_r = max(pad['sx'], pad['sy']) / 2.0
                dist = point_to_seg_dist(pad_pt, p1, p2)
                copper_clearance = dist - (pad_r + t_w / 2.0)
                if copper_clearance < min_clearance - 1e-4:
                    violations.append({
                        'type': 'track_pad_clearance',
                        'track_net': t_net,
                        'pad_ref': f"{ref}.{p_num}",
                        'pad_net': p_net,
                        'clearance': copper_clearance,
                        'pos': pad_pt
                    })

    # 2. Track vs Track of DIFFERENT net
    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):
            t1 = tracks[i]
            t2 = tracks[j]
            if t1['net'] == t2['net']:
                continue
            dist = seg_distance(t1['p1'], t1['p2'], t2['p1'], t2['p2'])
            copper_clearance = dist - (t1['width'] / 2.0 + t2['width'] / 2.0)
            if copper_clearance < min_clearance - 1e-4:
                violations.append({
                    'type': 'track_track_clearance',
                    'net1': t1['net'],
                    'net2': t2['net'],
                    'clearance': copper_clearance,
                    'p1': t1['p1'],
                    'p2': t2['p1']
                })
    return violations

