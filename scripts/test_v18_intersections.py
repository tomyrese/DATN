import sys
sys.path.append('scripts')
from solve_planar_pcb_v18 import paths
from test_routing_engine import segments_intersect

conflicts = 0
for i in range(len(paths)):
    s1 = paths[i]
    for j in range(i + 1, len(paths)):
        s2 = paths[j]
        if s1['net'] != s2['net']:
            if segments_intersect(s1['p1'], s1['p2'], s2['p1'], s2['p2']):
                print(f"CONFLICT between {s1['net']} ({s1['p1']}->{s1['p2']}) and {s2['net']} ({s2['p1']}->{s2['p2']})")
                conflicts += 1

print(f"Total track segments: {len(paths)}, Conflicts: {conflicts}")
