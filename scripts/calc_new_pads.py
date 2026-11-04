import math

# Footprint LEFT at (67.69, 68.8275, 90)
# Footprint RIGHT at (140.69, 68.8275, 90)
# Footprint Rasp_PI4 at (103.19, 94.8275, 0)

def rot90(x, y):
    # KiCad +90 deg rotation: x_rot = -y, y_rot = x
    # Wait, in KiCad 90 deg CCW: (x, y) -> (-y, x)?
    # Earlier we checked: Pad 10 (7.62, -6.35) -> world (61.34, 61.2075)
    # 67.69 + (-6.35) = 61.34
    # 68.8275 - 7.62 = 61.2075
    # So: x_world = fp_x + y_rel, y_world = fp_y - x_rel!
    return y, -x

# Let's verify:
# For new Pads 1..8: x_rel = +7.62
# y_world = fp_y - 7.62 = 68.8275 - 7.62 = 61.2075 (TOP ROW)
# For new Pads 9..16: x_rel = -7.62
# y_world = fp_y - (-7.62) = 68.8275 + 7.62 = 76.4475 (BOTTOM ROW)

print("=== NEW LEFT TB6612 PADS ===")
for p_num, y_rel, name in [
    (1, -8.89, "PWMA"), (2, -6.35, "AIN2"), (3, -3.81, "AIN1"), (4, -1.27, "STBY"),
    (5, 1.27, "BIN1"), (6, 3.81, "BIN2"), (7, 6.35, "PWMB"), (8, 8.89, "GND"),
    (9, -8.89, "VM"), (10, -6.35, "VCC"), (11, -3.81, "GND"), (12, -1.27, "AO1"),
    (13, 1.27, "AO2"), (14, 3.81, "BO2"), (15, 6.35, "BO1"), (16, 8.89, "GND")
]:
    x_rel = 7.62 if p_num <= 8 else -7.62
    xw = 67.69 + y_rel
    yw = 68.8275 - x_rel
    print(f"LEFT Pad {p_num:2d} ({name:5s}): ({xw:.2f}, {yw:.2f})")

print("\n=== NEW RIGHT TB6612 PADS ===")
for p_num, y_rel, name in [
    (1, -8.89, "PWMA"), (2, -6.35, "AIN2"), (3, -3.81, "AIN1"), (4, -1.27, "STBY"),
    (5, 1.27, "BIN1"), (6, 3.81, "BIN2"), (7, 6.35, "PWMB"), (8, 8.89, "GND"),
    (9, -8.89, "VM"), (10, -6.35, "VCC"), (11, -3.81, "GND"), (12, -1.27, "AO1"),
    (13, 1.27, "AO2"), (14, 3.81, "BO2"), (15, 6.35, "BO1"), (16, 8.89, "GND")
]:
    x_rel = 7.62 if p_num <= 8 else -7.62
    xw = 140.69 + y_rel
    yw = 68.8275 - x_rel
    print(f"RIGHT Pad {p_num:2d} ({name:5s}): ({xw:.2f}, {yw:.2f})")

