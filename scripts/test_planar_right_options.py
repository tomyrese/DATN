import math

# Test if 3 tracks of width 1.0mm with 0.5mm clearance can fit anywhere planar
# Clearance = 0.5mm
# Track width = 1.0mm
# Pad radius = 1.0mm (diameter 2.0mm)
# Required track center to pad center = 1.0 (pad) + 0.5 (clearance) + 0.5 (track) = 2.0mm
# Required track center to track center = 0.5 (track) + 0.5 (clearance) + 0.5 (track) = 1.5mm

# R4 Pad 2 is at (124.78, 65.4452)
# TB6612 Right Pad 9 is at (131.80, 76.4475)
# Between them in X: 131.80 - 124.78 = 7.02mm
# In Y, R4 is at 65.45, Pad 9 is at 76.45. They are separated in Y by 11.0mm!
print(f"Space between R4 Pad 2 and TB6612 Pad 9: dX = {131.80 - 124.78:.2f}mm, dY = {76.4475 - 65.4452:.2f}mm")

# If tracks run at X = 127.0, 128.5, 130.0:
for x in [127.0, 128.5, 130.0]:
    dist_r4 = abs(x - 124.78)
    dist_tb_p9 = abs(131.80 - x)
    cl_r4 = dist_r4 - 2.0
    cl_tb9 = dist_tb_p9 - 2.0
    print(f"Track at X={x}: clearance to R4 Pad 2 = {cl_r4:.2f}mm, clearance to TB Pad 9 = {cl_tb9:.2f}mm")

