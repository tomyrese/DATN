import math

# Pi4 pins in standard footprint:
# lx = -24.13 + col * 2.54, col = (pin - 1) // 2
# ly = -1.27 if (pin % 2 == 1) else 1.27
def get_pi_pad(x0, y0, rot, pin):
    col = (pin - 1) // 2
    row = (pin - 1) % 2
    lx = -24.13 + col * 2.54
    ly = -1.27 if row == 0 else 1.27
    rad = math.radians(rot)
    wx = x0 + lx * math.cos(rad) - ly * math.sin(rad)
    wy = y0 + lx * math.sin(rad) + ly * math.cos(rad)
    return round(wx, 2), round(wy, 2)

for rot in [0, 180]:
    print(f"=== ROT = {rot} ===")
    for p in [1, 3, 5, 6, 11, 13, 16, 18, 19, 21, 23, 32, 33, 35, 36, 37, 38]:
        pos = get_pi_pad(103.19, 94.83, rot, p)
        facing = "North" if pos[1] < 94.83 else "South"
        print(f"  Pin {p:2}: {pos} facing {facing}")

