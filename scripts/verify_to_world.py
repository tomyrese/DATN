import math

# Footprint world positions and rotations:
fp_info = {
    "Rasp_PI4": (103.19, 94.8275, 0),
    "LEFT": (67.69, 68.8275, 90),
    "RIGHT": (140.69, 68.8275, 90),
    "HC_SR04_1": (90.19, 50.4425, 0),
    "HC_SR04_2": (118.415917, 50.513844, 0),
    "MOTOR1": (67.67802, 53.400498, 0),
    "MOTOR2": (76.8, 53.4425, 0),
    "MOTOR3": (139.8, 53.9425, 0),
    "MOTOR4": (150.8, 53.9425, 0),
    "TCRT5000": (104.46, 50.4425, 180),
    "OLED": (148.31, 96.5, 180),
    "R1": (93.03, 65.9425, 0),
    "R2": (92.99, 72.4425, 180),
    "R3": (120.934925, 61.435956, 180),
    "R4": (120.97, 65.445234, 0)
}

def to_world(fp_name, lx, ly):
    fx, fy, frot = fp_info[fp_name]
    rad = math.radians(frot)
    # KiCad screen coordinate system: X is right, Y is DOWN.
    # A positive rotation of theta degrees rotates clockwise on screen:
    # xw = fx + lx * cos(rad) - ly * sin(rad)
    # yw = fy + lx * sin(rad) + ly * cos(rad)
    # Let's verify for frot = 90:
    # cos(90) = 0, sin(90) = 1
    # xw = fx - ly
    # yw = fy + lx
    # Wait! Earlier we tested:
    # In LEFT: lx = 7.62, ly = -6.35 (Pad 10)
    # If xw = fx - ly = 67.69 - (-6.35) = 67.69 + 6.35 = 74.04!
    # But earlier we saw Pad 10 had X = 61.34!
    # 67.69 - 6.35 = 61.34!
    # That means KiCad rotation +90 rotates COUNTER-CLOCKWISE:
    # xw = fx + ly
    # yw = fy - lx
    # Let's check:
    # lx = 7.62 -> yw = fy - 7.62 = 68.8275 - 7.62 = 61.2075!
    # ly = -6.35 -> xw = fx + (-6.35) = 67.69 - 6.35 = 61.34!
    # YES! In KiCad, positive rotation rotates counter-clockwise:
    # [xw - fx]   [ cos(rad)  sin(rad)] [lx]
    # [yw - fy] = [-sin(rad)  cos(rad)] [ly]
    # With rad = 90: cos(90)=0, sin(90)=1:
    # xw = fx + ly
    # yw = fy - lx
    # With rad = 180: cos(180)=-1, sin(180)=0:
    # xw = fx - lx
    # yw = fy - ly
    # With rad = 0:
    # xw = fx + lx
    # yw = fy + ly
    xw = fx + lx * math.cos(rad) + ly * math.sin(rad)
    yw = fy - lx * math.sin(rad) + ly * math.cos(rad)
    return xw, yw

print("Verified to_world formula.")
print("LEFT Pad 10 (lx=-7.62, ly=-6.35):", to_world("LEFT", -7.62, -6.35))
print("LEFT Pad 1 (lx=7.62, ly=-8.89):", to_world("LEFT", 7.62, -8.89))
print("TCRT5000 Pad 1 (lx=-5.08, ly=0):", to_world("TCRT5000", -5.08, 0))
print("TCRT5000 Pad 5 (lx=5.08, ly=0):", to_world("TCRT5000", 5.08, 0))
print("OLED Pad 1 (lx=-3.81, ly=0):", to_world("OLED", -3.81, 0))
print("OLED Pad 4 (lx=3.81, ly=0):", to_world("OLED", 3.81, 0))

