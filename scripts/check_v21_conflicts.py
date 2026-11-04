import math
import solve_planar_pcb_v21 as v21

def dist_pt_seg(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    l2 = dx*dx + dy*dy
    if l2 < 1e-8:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax)*dx + (py - ay)*dy) / l2))
    projx = ax + t * dx
    projy = ay + t * dy
    return math.hypot(px - projx, py - projy)

def seg_seg_dist(p1, p2, q1, q2):
    # Check if lines intersect
    def ccw(A,B,C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    def intersect(A,B,C,D):
        return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
    
    if intersect(p1, p2, q1, q2):
        return 0.0
    
    d1 = dist_pt_seg(p1, q1, q2)
    d2 = dist_pt_seg(p2, q1, q2)
    d3 = dist_pt_seg(q1, p1, p2)
    d4 = dist_pt_seg(q2, p1, p2)
    return min(d1, d2, d3, d4)

conflicts = []
paths = v21.paths

for i in range(len(paths)):
    s1 = paths[i]
    for j in range(i + 1, len(paths)):
        s2 = paths[j]
        if s1['net'] == s2['net']:
            continue
        
        # Check endpoints sharing
        # If they share an endpoint of same net, ok, but different net means short!
        d = seg_seg_dist(s1['p1'], s1['p2'], s2['p1'], s2['p2'])
        req_clearance = (s1['width'] + s2['width']) / 2.0 + 0.45 # safe margin
        if d < req_clearance:
            conflicts.append((s1, s2, d))

print(f"Total track segments: {len(paths)}")
print(f"Total conflicts found: {len(conflicts)}")
for s1, s2, d in conflicts[:20]:
    print(f"CONFLICT between {s1['net']} ({s1['p1']}->{s1['p2']}) and {s2['net']} ({s2['p1']}->{s2['p2']}): dist={d:.3f}")

