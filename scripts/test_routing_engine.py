"""
Conflict resolution tester for Pi4 Robot Carrier PCB
"""
from solve_planar_pcb_v3 import (
    segments_intersect, pi_odd, pi_even, tb1, tb2, m1, m2, m3, m4,
    tcrt, us1, us2, r1, r2, r3, r4, oled
)

def test_routing(routing_fn):
    paths = []
    def add(net, pts, width=0.6):
        for i in range(len(pts)-1):
            paths.append({
                'net': net,
                'p1': (round(pts[i][0], 4), round(pts[i][1], 4)),
                'p2': (round(pts[i+1][0], 4), round(pts[i+1][1], 4)),
                'width': width
            })
    routing_fn(add)
    
    conflicts = []
    for i in range(len(paths)):
        for j in range(i+1, len(paths)):
            s1 = paths[i]
            s2 = paths[j]
            if s1['net'] != s2['net']:
                if segments_intersect(s1['p1'], s1['p2'], s2['p1'], s2['p2']):
                    conflicts.append((s1, s2))
    print(f"Total segments: {len(paths)}, Conflicts: {len(conflicts)}")
    for s1, s2 in conflicts[:15]:
        print(f"  {s1['net']} ({s1['p1']}->{s1['p2']}) x {s2['net']} ({s2['p1']}->{s2['p2']})")
    return len(conflicts), paths

print("Tester loaded.")
