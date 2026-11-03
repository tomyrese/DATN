import math

def get_abs_pos(fp_x, fp_y, fp_rot, pad_x, pad_y, pad_rot):
    # KiCad rotation is counter-clockwise in math, but Y points down!
    # In KiCad PCB, a footprint rotated by rot degrees:
    # angle in radians:
    rad = math.radians(fp_rot)
    # Standard 2D rotation where Y is inverted or standard?
    # In KiCad: x_new = x*cos(rad) - y*sin(rad), y_new = x*sin(rad) + y*cos(rad)
    x_rot = pad_x * math.cos(rad) - pad_y * math.sin(rad)
    y_rot = pad_x * math.sin(rad) + pad_y * math.cos(rad)
    return fp_x + x_rot, fp_y + y_rot

# Let's test with LEFT footprint: fp_x=67.69, fp_y=68.8275, fp_rot=90
# Pad 1: pad_x=-7.62, pad_y=-8.89
# If rad = 90 deg:
for p_num, px, py in [(1, -7.62, -8.89), (8, -7.62, 8.89), (9, 7.62, -8.89), (16, 7.62, 8.89)]:
    x1, y1 = get_abs_pos(67.69, 68.8275, 90, px, py, 90)
    print(f"Pad {p_num}: ({x1:.4f}, {y1:.4f})")
