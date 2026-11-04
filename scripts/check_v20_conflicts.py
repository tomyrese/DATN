import sys
sys.path.append('scripts')
import solve_planar_pcb_v20 as v20
from test_routing_engine import segments_intersect

paths = v20.paths
conflicts = []
for i in range(len(paths)):
    for j in range(i + 1, len(paths)):
        p1 = paths[i]
        p2 = paths[j]
        if p1['net'] == p2['net']:
            continue
        p1_start, p1_end = p1['p1'], p1['p2']
        p2_start, p2_end = p2['p1'], p2['p2']
        if segments_intersect(p1_start, p1_end, p2_start, p2_end):
            conflicts.append((p1, p2))

print(f"Total v20 conflicts: {len(conflicts)}")
for c in conflicts:
    print(f"Conflict between {c[0]['net']} ({c[0]['p1']}->{c[0]['p2']}) and {c[1]['net']} ({c[1]['p1']}->{c[1]['p2']})")
