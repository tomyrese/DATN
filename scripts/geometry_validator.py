import math
import json

with open('scripts/parsed_world_pads.json', 'r', encoding='utf-8') as f:
    fps = json.load(f)

# Flatten all pads
all_pads = []
for ref, f_data in fps.items():
    for pnum, p in f_data['pads'].items():
        all_pads.append({
            'ref': ref,
            'pnum': pnum,
            'x': p['wx'],
            'y': p['wy'],
            'net_id': p['net_id'],
            'net_name': p['net_name'],
            'radius': p['size'][0] / 2.0
        })

print(f"Total pads loaded: {len(all_pads)}")

def point_to_segment_dist(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    l2 = dx*dx + dy*dy
    if l2 < 1e-9:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1)*dx + (py - y1)*dy) / l2))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)

def segments_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
    
    # Check bounding box first
    if max(min(x1, x2), min(x3, x4)) > min(max(x1, x2), max(x3, x4)):
        return False
    if max(min(y1, y2), min(y3, y4)) > min(max(y1, y2), max(y3, y4)):
        return False
        
    c1 = ccw(x1, y1, x3, y3, x4, y4)
    c2 = ccw(x2, y2, x3, y3, x4, y4)
    c3 = ccw(x1, y1, x2, y2, x3, y3)
    c4 = ccw(x1, y1, x2, y2, x4, y4)
    return (c1 != c2) and (c3 != c4)

def seg_seg_dist(x1, y1, x2, y2, x3, y3, x4, y4):
    if segments_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
        return 0.0
    return min(
        point_to_segment_dist(x1, y1, x3, y3, x4, y4),
        point_to_segment_dist(x2, y2, x3, y3, x4, y4),
        point_to_segment_dist(x3, y3, x1, y1, x2, y2),
        point_to_segment_dist(x4, y4, x1, y1, x2, y2)
    )

def test_track(seg, existing_tracks, all_pads, min_clearance=0.50):
    sx1, sy1 = seg['p1']
    sx2, sy2 = seg['p2']
    s_net = seg['net_name']
    s_w = seg['width']
    
    # 1. Check against all pads of DIFFERENT nets
    for p in all_pads:
        if p['net_name'] == s_net:
            continue
        d = point_to_segment_dist(p['x'], p['y'], sx1, sy1, sx2, sy2)
        req_d = (s_w / 2.0) + p['radius'] + min_clearance
        if d < req_d - 1e-4:
            return False, f"Pad clearance violation with {p['ref']}.{p['pnum']} ({p['net_name']}): dist={d:.3f} < req={req_d:.3f}"
            
    # 2. Check against all pads of SAME net (endpoints must match pad)
    # 3. Check against existing tracks
    for ot in existing_tracks:
        ox1, oy1 = ot['p1']
        ox2, oy2 = ot['p2']
        o_net = ot['net_name']
        o_w = ot['width']
        
        # If same net, they can connect at endpoints
        if o_net == s_net:
            # check if they intersect other than at endpoints
            pass
        else:
            # Different net: must not cross and must maintain clearance
            if segments_intersect(sx1, sy1, sx2, sy2, ox1, oy1, ox2, oy2):
                return False, f"Crossing different net {o_net}"
            d = seg_seg_dist(sx1, sy1, sx2, sy2, ox1, oy1, ox2, oy2)
            req_d = (s_w + o_w) / 2.0 + min_clearance
            if d < req_d - 1e-4:
                return False, f"Track clearance violation with {o_net}: dist={d:.3f} < req={req_d:.3f}"
                
    return True, "OK"

print("Geometry validator ready.")
