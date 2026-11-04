import math

# Pad positions in footprint:
# Pad 1: (-7.62, -8.89), Pad 8: (-7.62, 8.89)
# Pad 9: (7.62, -8.89), Pad 16: (7.62, 8.89)

def get_pads(rot_deg):
    rad = math.radians(rot_deg)
    # KiCad rotates: x' = x*cos(rad) - y*sin(rad), y' = x*sin(rad) + y*cos(rad)
    # Wait, in KiCad screen coordinates, Y is down!
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    pads = {}
    for i in range(1, 9):
        x = -7.62
        y = -8.89 + (i - 1) * 2.54
        xp = x * cos_a - y * sin_a
        yp = x * sin_a + y * cos_a
        pads[i] = (round(xp, 2), round(yp, 2))
    for i in range(9, 17):
        x = 7.62
        y = -8.89 + (i - 9) * 2.54
        xp = x * cos_a - y * sin_a
        yp = x * sin_a + y * cos_a
        pads[i] = (round(xp, 2), round(yp, 2))
    return pads

print("--- rot = 90 ---")
p90 = get_pads(90)
for i in [1, 8, 9, 16]:
    print(f"Pad {i:2}: {p90[i]}")

print("\n--- rot = 270 ---")
p270 = get_pads(270)
for i in [1, 8, 9, 16]:
    print(f"Pad {i:2}: {p270[i]}")

