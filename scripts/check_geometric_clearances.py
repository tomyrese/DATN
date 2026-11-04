import math, json

# Import pads and paths
import simulate_perfect_routing as sim
from simulate_perfect_routing import paths, pi_odd, pi_even, tb1, tb2, m1, m2, m3, m4, tcrt, us1, us2, r1, r2, r3, r4, oled

# Load all pads with their net names and coordinates
with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    wp = json.load(f)

# Jumpers
jumpers = [
    ("JMP1_SDA", "/I2C_SDA", (94.30, 87.00), (144.50, 87.00), "J1: SDA"),
    ("JMP2_SCL", "/I2C_SCL", (94.30, 99.00), (147.04, 99.00), "J2: SCL"),
    ("JMP3_3V3", "/+3V3_LOGIC", (107.00, 84.00), (152.12, 88.00), "J3: 3V3"),
    ("JMP4_STBY_L", "/STBY_L", (66.42, 58.00), (81.60, 99.00), "J4: STBY-L"),
    ("JMP5_STBY_R", "/STBY_R", (139.42, 58.00), (114.62, 85.00), "J5: STBY-R"),
    ("JMP6_VM", "/VM_MOTOR", (58.80, 74.00), (131.80, 74.00), "J6: VM"),
    ("JMP7_ECHO_R", "/ECHO_R", (117.16, 68.00), (112.08, 88.00), "J7: ECHO-R"),
    ("JMP8_GND_R", "GND", (149.58, 69.00), (149.58, 90.00), "J8: GND-R"),
    ("JMP9_GND_PI", "GND", (96.84, 89.00), (96.84, 99.00), "J9: GND-PI"),
    ("JMP10_5V_L", "/+5V_PWR", (61.34, 43.50), (61.34, 74.00), "J10: +5V-L"),
    ("JMP11_5V_R", "/+5V_PWR", (127.32, 99.00), (134.34, 74.00), "J11: +5V-R"),
    ("JMP12_GND_TOP", "GND", (94.00, 62.00), (91.76, 99.00), "J12: GND-TOP"),
    ("JMP13_GND_US2", "GND", (127.00, 67.50), (136.88, 73.00), "J13: GND-US2"),
    ("JMP14_PWM_R", "/PWMA_R", (131.80, 57.00), (124.78, 88.00), "J14: PWM-R"),
    ("JMP15_IN2_R", "/AIN2_R", (134.34, 57.00), (122.24, 86.00), "J15: IN2-R"),
    ("JMP16_IN1_R", "/AIN1_R", (136.88, 57.00), (119.70, 84.00), "J16: IN1-R"),
    ("JMP17_TRIG_L", "/TRIG_L", (88.92, 53.50), (89.22, 90.00), "J17: TRIG-L"),
]

vias = []
for jmp, net, v1, v2, lbl in jumpers:
    vias.append({'net': net, 'pos': v1, 'name': f"{jmp}_1"})
    vias.append({'net': net, 'pos': v2, 'name': f"{jmp}_2"})

print(f"Total via count: {len(vias)}")

def pt_seg_dist(p, a, b):
    px, py = p
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    nearest_x = ax + t * dx
    nearest_y = ay + t * dy
    return math.hypot(px - nearest_x, py - nearest_y)

# Build all pads list from the swapped footprints mapping
all_pads = []
# TB Left
tb1_nets = {1: "/PWMA_L", 2: "/AIN2_L", 3: "/AIN1_L", 4: "/STBY_L", 5: "/AIN1_L", 6: "/AIN2_L", 7: "/PWMA_L", 8: "GND",
            9: "/VM_MOTOR", 10: "/+5V_PWR", 11: "GND", 12: "/M1_A", 13: "/M1_B", 14: "/M2_B", 15: "/M2_A", 16: "GND"}
for k, v in tb1.items():
    all_pads.append({'ref': 'LEFT', 'pad': k, 'net': tb1_nets[k], 'pos': v})

# TB Right
tb2_nets = {1: "/PWMA_R", 2: "/AIN2_R", 3: "/AIN1_R", 4: "/STBY_R", 5: "/AIN1_R", 6: "/AIN2_R", 7: "/PWMA_R", 8: "GND",
            9: "/VM_MOTOR", 10: "/+5V_PWR", 11: "GND", 12: "/M3_A", 13: "/M3_B", 14: "/M4_B", 15: "/M4_A", 16: "GND"}
for k, v in tb2.items():
    all_pads.append({'ref': 'RIGHT', 'pad': k, 'net': tb2_nets[k], 'pos': v})

# Pi 4
pi_nets = {
    37: "/PWMA_L", 35: "/AIN2_L", 33: "/AIN1_L", 38: "/STBY_L", 31: "/TRIG_L", 29: "/ECHO_L",
    3: "/PWMA_R", 5: "/AIN2_R", 7: "/AIN1_R", 11: "/STBY_R", 15: "/TRIG_R", 13: "/ECHO_R",
    19: "/LINE_L", 21: "/LINE_C", 23: "/LINE_R", 27: "/I2C_SDA", 28: "/I2C_SCL",
    2: "/+5V_PWR", 4: "/+5V_PWR", 6: "GND", 9: "GND", 14: "GND", 20: "GND", 25: "GND",
    30: "GND", 34: "GND", 39: "GND", 40: "GND", 17: "/+3V3_LOGIC"
}
for pin in range(1, 41):
    if pin % 2 == 1:
        pos = pi_odd(pin)
    else:
        pos = pi_even(pin)
    net = pi_nets.get(pin, "NC")
    all_pads.append({'ref': 'Rasp_PI4', 'pad': pin, 'net': net, 'pos': pos})

# Check Via to Via clearance
via_radius = 1.0 # size 2.0mm
track_clearance = 0.50

via_violations = []
for i in range(len(vias)):
    for j in range(i + 1, len(vias)):
        v1 = vias[i]
        v2 = vias[j]
        if v1['net'] == v2['net']:
            continue
        dist = math.hypot(v1['pos'][0] - v2['pos'][0], v1['pos'][1] - v2['pos'][1])
        clearance = dist - (via_radius * 2)
        if clearance < track_clearance - 0.01:
            via_violations.append((v1, v2, clearance))

print(f"Via-to-Via clearance violations (< 0.50mm): {len(via_violations)}")
for v in via_violations:
    print(f"  VIOLATION: {v[0]['name']} ({v[0]['net']}) vs {v[1]['name']} ({v[1]['net']}), clearance: {v[2]:.2f}mm")

# Check Via to Pad clearance
via_pad_violations = []
pad_radius = 1.0 # size 2.0mm
for v in vias:
    for p in all_pads:
        if p['net'] == "NC" or p['net'] == v['net']:
            continue
        dist = math.hypot(v['pos'][0] - p['pos'][0], v['pos'][1] - p['pos'][1])
        clearance = dist - (via_radius + pad_radius)
        if clearance < track_clearance - 0.01:
            via_pad_violations.append((v, p, clearance))

print(f"Via-to-Pad clearance violations (< 0.50mm): {len(via_pad_violations)}")
for vp in via_pad_violations:
    print(f"  VIOLATION: Via {vp[0]['name']} ({vp[0]['net']} at {vp[0]['pos']}) vs Pad {vp[1]['ref']} pin {vp[1]['pad']} ({vp[1]['net']} at {vp[1]['pos']}), clearance: {vp[2]:.2f}mm")

# Check Track to Pad clearance (avoiding track connecting to the pad itself)
track_pad_violations = []
for t in paths:
    t_half_w = t['width'] / 2.0
    for p in all_pads:
        if p['net'] == "NC" or p['net'] == t['net']:
            continue
        dist = pt_seg_dist(p['pos'], t['p1'], t['p2'])
        clearance = dist - (pad_radius + t_half_w)
        if clearance < track_clearance - 0.01:
            track_pad_violations.append((t, p, clearance))

print(f"Track-to-Pad clearance violations (< 0.50mm): {len(track_pad_violations)}")
for tp in track_pad_violations[:10]:
    print(f"  VIOLATION: Track {tp[0]['net']} ({tp[0]['p1']}->{tp[0]['p2']}) vs Pad {tp[1]['ref']} pin {tp[1]['pad']} ({tp[1]['net']} at {tp[1]['pos']}), clearance: {tp[2]:.2f}mm")

# Check Track to Via clearance
track_via_violations = []
for t in paths:
    t_half_w = t['width'] / 2.0
    for v in vias:
        if v['net'] == t['net']:
            continue
        dist = pt_seg_dist(v['pos'], t['p1'], t['p2'])
        clearance = dist - (via_radius + t_half_w)
        if clearance < track_clearance - 0.01:
            track_via_violations.append((t, v, clearance))

print(f"Track-to-Via clearance violations (< 0.50mm): {len(track_via_violations)}")
for tv in track_via_violations[:10]:
    print(f"  VIOLATION: Track {tv[0]['net']} ({tv[0]['p1']}->{tv[0]['p2']}) vs Via {tv[1]['name']} ({tv[1]['net']} at {tv[1]['pos']}), clearance: {tv[2]:.2f}mm")
