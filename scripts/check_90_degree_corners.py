import math
import simulate_perfect_routing as sim
from simulate_perfect_routing import paths

# Check for 90 degree corners in paths
# A corner is formed by two segments sharing a point
points_map = {}
for idx, p in enumerate(paths):
    p1 = p['p1']
    p2 = p['p2']
    net = p['net']
    points_map.setdefault((p1, net), []).append((p2, idx))
    points_map.setdefault((p2, net), []).append((p1, idx))

orthogonal_turns = []
for (pt, net), neighbors in points_map.items():
    if len(neighbors) == 2:
        n1 = neighbors[0][0]
        n2 = neighbors[1][0]
        v1 = (n1[0] - pt[0], n1[1] - pt[1])
        v2 = (n2[0] - pt[0], n2[1] - pt[1])
        len1 = math.hypot(v1[0], v1[1])
        len2 = math.hypot(v2[0], v2[1])
        if len1 > 1e-4 and len2 > 1e-4:
            dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (len1 * len2)
            # If dot is near 0 (|dot| < 0.2), it is approximately 90 degrees!
            if abs(dot) < 0.2:
                orthogonal_turns.append((pt, net, dot, neighbors[0][1], neighbors[1][1]))

print(f"Total 90-degree corners in paths: {len(orthogonal_turns)}")
for ot in orthogonal_turns:
    print(f"  90-degree corner at {ot[0]} for net {ot[1]}")

