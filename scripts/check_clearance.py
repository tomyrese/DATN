from solve_planar_pcb_v16 import paths
from solve_planar_pcb_v3 import (
    pt_seg_dist, pi_odd, pi_even, tb1, tb2, m1, m2, m3, m4,
    tcrt, us1, us2, r1, r2, r3, r4, oled
)

# Collect all pads and their nets
pads = []
for i in range(1, 41):
    if i % 2 == 1:
        pads.append(('Rasp_PI4', str(i), pi_odd(i)))
    else:
        pads.append(('Rasp_PI4', str(i), pi_even(i)))

for k, pt in tb1.items():
    pads.append(('LEFT', str(k), pt))
for k, pt in tb2.items():
    pads.append(('RIGHT', str(k), pt))
for k, pt in m1.items():
    pads.append(('MOTOR1', str(k), pt))
for k, pt in m2.items():
    pads.append(('MOTOR2', str(k), pt))
for k, pt in m3.items():
    pads.append(('MOTOR3', str(k), pt))
for k, pt in m4.items():
    pads.append(('MOTOR4', str(k), pt))
for k, pt in tcrt.items():
    pads.append(('TCRT5000', str(k), pt))
for k, pt in us1.items():
    pads.append(('HC_SR04_1', str(k), pt))
for k, pt in us2.items():
    pads.append(('HC_SR04_2', str(k), pt))
for k, pt in r1.items():
    pads.append(('R1', str(k), pt))
for k, pt in r2.items():
    pads.append(('R2', str(k), pt))
for k, pt in r3.items():
    pads.append(('R3', str(k), pt))
for k, pt in r4.items():
    pads.append(('R4', str(k), pt))
for k, pt in oled.items():
    pads.append(('OLED', str(k), pt))

# Check track-to-pad clearances (for pads not on the same net/endpoint)
pad_clearance_violations = 0
for comp, pad_num, pad_pt in pads:
    for s in paths:
        # If pad is endpoint of s, skip
        if (abs(pad_pt[0] - s['p1'][0]) < 0.05 and abs(pad_pt[1] - s['p1'][1]) < 0.05) or \
           (abs(pad_pt[0] - s['p2'][0]) < 0.05 and abs(pad_pt[1] - s['p2'][1]) < 0.05):
            continue
        dist = pt_seg_dist(pad_pt, s['p1'], s['p2'])
        pad_radius = 0.8  # 1.6mm pad
        track_half_width = s['width'] / 2.0
        clearance = dist - pad_radius - track_half_width
        if clearance < 0.20:
            print(f"Clearance issue: Pad {comp}:{pad_num} at {pad_pt} to {s['net']} ({s['p1']}->{s['p2']}): dist={dist:.3f}, clear={clearance:.3f}mm")
            pad_clearance_violations += 1

print(f"Total track-to-pad clearance violations: {pad_clearance_violations}")
