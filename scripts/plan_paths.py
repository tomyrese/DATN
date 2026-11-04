import json

with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    wp = json.load(f)

def pad_pt(ref, pad_num):
    p = wp[ref][str(pad_num)]
    return (p['x'], p['y'])

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    # Check bounding boxes first
    if max(A[0], B[0]) < min(C[0], D[0]) or max(C[0], D[0]) < min(A[0], B[0]):
        return False
    if max(A[1], B[1]) < min(C[1], D[1]) or max(C[1], D[1]) < min(A[1], B[1]):
        return False
    # If shared endpoint
    eps = 1e-4
    for p1 in [A, B]:
        for p2 in [C, D]:
            if abs(p1[0]-p2[0]) < eps and abs(p1[1]-p2[1]) < eps:
                return False
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

print("Path checker ready.")

