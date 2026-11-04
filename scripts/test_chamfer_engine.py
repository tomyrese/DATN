import math

def chamfer_path(pts, d=1.5):
    """
    Takes a list of points [(x0, y0), (x1, y1), ...] representing an orthogonal
    or mixed path, and replaces any 90-degree corner at p_i with two 45-degree
    points, so that no corner has a 90-degree angle.
    """
    if len(pts) <= 2:
        return pts
    
    new_pts = [pts[0]]
    for i in range(1, len(pts) - 1):
        prev_p = new_pts[-1]
        curr_p = pts[i]
        next_p = pts[i+1]
        
        v1 = (curr_p[0] - prev_p[0], curr_p[1] - prev_p[1])
        v2 = (next_p[0] - curr_p[0], next_p[1] - curr_p[1])
        
        len1 = math.hypot(v1[0], v1[1])
        len2 = math.hypot(v2[0], v2[1])
        
        if len1 < 1e-4 or len2 < 1e-4:
            continue
            
        # Check if v1 and v2 are perpendicular (dot product near 0)
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        cos_theta = dot / (len1 * len2)
        
        # If angle is approx 90 degrees (cos_theta between -0.2 and 0.2)
        if abs(cos_theta) < 0.2:
            # Determine chamfer distance
            # Cannot exceed 40% of either segment
            actual_d = min(d, len1 * 0.45, len2 * 0.45)
            
            p_in = (
                round(curr_p[0] - (v1[0] / len1) * actual_d, 4),
                round(curr_p[1] - (v1[1] / len1) * actual_d, 4)
            )
            p_out = (
                round(curr_p[0] + (v2[0] / len2) * actual_d, 4),
                round(curr_p[1] + (v2[0] / len2) * actual_d, 4)
            )
            new_pts.append(p_in)
            new_pts.append(p_out)
        else:
            new_pts.append(curr_p)
            
    new_pts.append(pts[-1])
    return new_pts

# Test with a simple L-turn
orig = [(0, 0), (10, 0), (10, 10)]
chamf = chamfer_path(orig, d=2.0)
print("Original:", orig)
print("Chamfered:", chamf)

