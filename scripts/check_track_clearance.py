from solve_planar_pcb_v16 import paths
from solve_planar_pcb_v3 import pt_seg_dist

def seg_seg_dist(p1, p2, p3, p4):
    # Distance between segment p1-p2 and segment p3-p4
    # Minimum of pt_seg_dist for all 4 endpoints
    d1 = pt_seg_dist(p1, p3, p4)
    d2 = pt_seg_dist(p2, p3, p4)
    d3 = pt_seg_dist(p3, p1, p2)
    d4 = pt_seg_dist(p4, p1, p2)
    return min(d1, d2, d3, d4)

violations = 0
for i in range(len(paths)):
    s1 = paths[i]
    for j in range(i + 1, len(paths)):
        s2 = paths[j]
        if s1['net'] == s2['net']:
            continue
        
        # Check distance between non-touching segments
        d = seg_seg_dist(s1['p1'], s1['p2'], s2['p1'], s2['p2'])
        w1 = s1['width'] / 2.0
        w2 = s2['width'] / 2.0
        clearance = d - w1 - w2
        if clearance < 0.20:
            print(f"Track-track clearance issue: {s1['net']} ({s1['p1']}->{s1['p2']}) to {s2['net']} ({s2['p1']}->{s2['p2']}): dist={d:.3f}, clear={clearance:.3f}mm")
            violations += 1

print(f"Total track-to-track clearance violations (<0.20mm): {violations}")
