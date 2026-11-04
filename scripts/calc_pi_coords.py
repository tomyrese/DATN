# Pi4 header: PinSocket_2x20_P2.54mm_Vertical
# In footprint:
# Pad 1: (-24.13, -1.27), Pad 2: (-24.13, 1.27)
# Pad 3: (-21.59, -1.27), Pad 4: (-21.59, 1.27)
# ...
# Pad 39: (24.13, -1.27), Pad 40: (24.13, 1.27)

def calc_pi_pins(x0, y0, rot):
    import math
    rad = math.radians(rot)
    cos_a = round(math.cos(rad))
    sin_a = round(math.sin(rad))
    pins = {}
    for pin in range(1, 41):
        col = (pin - 1) // 2  # 0 to 19
        row = (pin - 1) % 2   # 0 (odd) or 1 (even)
        lx = -24.13 + col * 2.54
        ly = -1.27 if row == 0 else 1.27
        wx = x0 + lx * cos_a - ly * sin_a
        wy = y0 + lx * sin_a + ly * cos_a
        pins[pin] = (round(wx, 2), round(wy, 2))
    return pins

print("=== Rasp_PI4 at (103.19, 94.83) rot=0 ===")
p0 = calc_pi_pins(103.19, 94.83, 0)
print(f"Pin 1:  {p0[1]} (Odd,  Row 0)")
print(f"Pin 2:  {p0[2]} (Even, Row 1)")
print(f"Pin 39: {p0[39]} (Odd,  Row 0)")
print(f"Pin 40: {p0[40]} (Even, Row 1)")
print(f"Pin 32: {p0[32]}")
print(f"Pin 33: {p0[33]}")
print(f"Pin 35: {p0[35]}")
print(f"Pin 36: {p0[36]}")
print(f"Pin 37: {p0[37]}")
print(f"Pin 38: {p0[38]}")

print("\n=== Rasp_PI4 at (103.19, 94.83) rot=180 ===")
p180 = calc_pi_pins(103.19, 94.83, 180)
print(f"Pin 1:  {p180[1]}")
print(f"Pin 2:  {p180[2]}")
print(f"Pin 39: {p180[39]}")
print(f"Pin 40: {p180[40]}")
print(f"Pin 32: {p180[32]}")
print(f"Pin 33: {p180[33]}")
print(f"Pin 35: {p180[35]}")
print(f"Pin 36: {p180[36]}")
print(f"Pin 37: {p180[37]}")
print(f"Pin 38: {p180[38]}")

