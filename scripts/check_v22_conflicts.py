import sys
sys.path.append('scripts')
import solve_planar_pcb_v22 as v22
import check_v21_conflicts as chk

paths = v22.paths
conflicts = []
for i in range(len(paths)):
    s1 = paths[i]
    for j in range(i + 1, len(paths)):
        s2 = paths[j]
        if s1['net'] == s2['net']:
            continue
        d = chk.seg_seg_dist(s1['p1'], s1['p2'], s2['p1'], s2['p2'])
        req = (s1['width'] + s2['width']) / 2.0 + 0.45
        if d < req:
            conflicts.append((s1, s2, d))

print(f"Total track segments: {len(paths)}")
print(f"Total conflicts found: {len(conflicts)}")
for s1, s2, d in conflicts[:30]:
    print(f"CONFLICT between {s1['net']} ({s1['p1']}->{s1['p2']}) and {s2['net']} ({s2['p1']}->{s2['p2']}): dist={d:.3f}")

