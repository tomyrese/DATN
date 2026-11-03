from solve_planar_pcb_v13 import paths
from solve_planar_pcb_v3 import pt_seg_dist, pi_odd, pi_even, tb1, tb2, m1, m2, m3, m4, tcrt, us1, us2, r1, r2, r3, r4, oled
import math

jumpers = [
    ("JMP1_SDA", "/I2C_SDA", (94.30, 87.00), (144.50, 87.00)),
    ("JMP2_SCL", "/I2C_SCL", (94.30, 99.00), (147.04, 99.00)),
    ("JMP3_3V3", "/+3V3_LOGIC", (107.00, 84.00), (152.12, 88.00)),
    ("JMP4_STBY_L", "/STBY_L", (66.42, 58.00), (81.60, 99.00)),
    ("JMP5_STBY_R", "/STBY_R", (139.42, 58.00), (114.62, 85.00)),
    ("JMP6_VM", "/VM_MOTOR", (58.80, 74.00), (131.80, 74.00)),
    ("JMP7_ECHO_R", "/ECHO_R", (124.78, 67.50), (112.08, 88.00)),
    ("JMP8_GND_R", "GND", (149.58, 69.00), (149.58, 90.00)),
    ("JMP9_GND_PI", "GND", (96.84, 89.00), (96.84, 99.00)),
]

vias = []
for name, net, v1, v2 in jumpers:
    vias.append((name + "_A", net, v1))
    vias.append((name + "_B", net, v2))

# 1. Check via to via distance
print("Checking via to via distance...")
for i in range(len(vias)):
    n1, net1, p1 = vias[i]
    for j in range(i+1, len(vias)):
        n2, net2, p2 = vias[j]
        d = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
        if d < 2.0:
            print(f"Via-Via proximity: {n1} ({p1}) and {n2} ({p2}), d={d:.3f}mm")

# 2. Check via to pads distance
print("\nChecking via to pads distance...")
pads = []
for i in range(1, 41):
    pads.append(('Rasp_PI4', str(i), pi_odd(i) if i%2==1 else pi_even(i)))
for k, pt in tb1.items(): pads.append(('LEFT', str(k), pt))
for k, pt in tb2.items(): pads.append(('RIGHT', str(k), pt))
for k, pt in m1.items(): pads.append(('MOTOR1', str(k), pt))
for k, pt in m2.items(): pads.append(('MOTOR2', str(k), pt))
for k, pt in m3.items(): pads.append(('MOTOR3', str(k), pt))
for k, pt in m4.items(): pads.append(('MOTOR4', str(k), pt))
for k, pt in tcrt.items(): pads.append(('TCRT5000', str(k), pt))
for k, pt in us1.items(): pads.append(('HC_SR04_1', str(k), pt))
for k, pt in us2.items(): pads.append(('HC_SR04_2', str(k), pt))
for k, pt in r1.items(): pads.append(('R1', str(k), pt))
for k, pt in r2.items(): pads.append(('R2', str(k), pt))
for k, pt in r3.items(): pads.append(('R3', str(k), pt))
for k, pt in r4.items(): pads.append(('R4', str(k), pt))
for k, pt in oled.items(): pads.append(('OLED', str(k), pt))

via_radius = 0.8 # 1.6mm via
pad_radius = 0.8 # 1.6mm pad

for vn, vnet, vp in vias:
    for comp, pnum, pp in pads:
        d = math.hypot(vp[0]-pp[0], vp[1]-pp[1])
        clearance = d - via_radius - pad_radius
        if clearance < 0.20:
            print(f"Via-Pad proximity: {vn} ({vp}) to {comp}:{pnum} ({pp}), d={d:.3f}, clear={clearance:.3f}mm")

# 3. Check via to tracks of other nets
print("\nChecking via to tracks distance...")
for vn, vnet, vp in vias:
    for s in paths:
        if s['net'] == vnet:
            continue
        d = pt_seg_dist(vp, s['p1'], s['p2'])
        clearance = d - via_radius - (s['width']/2.0)
        if clearance < 0.20:
            print(f"Via-Track proximity: {vn} ({vp}) to {s['net']} ({s['p1']}->{s['p2']}), d={d:.3f}, clear={clearance:.3f}mm")

print("\nVia clearance check complete.")
