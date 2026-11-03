import json, re, uuid, math

def segments_intersect(p1, p2, p3, p4):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    
    if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4:
        return False
        
    return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))

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

# Pad positions
# Pi4
pi_odd_y = 93.5575
pi_even_y = 96.0975

def pi_odd(pin):
    # Pin 1 is at 127.32, Pin 39 is at 79.06
    return (round(127.32 - (pin - 1) * 1.27, 4), pi_odd_y)

def pi_even(pin):
    # Pin 2 is at 127.32, Pin 40 is at 79.06
    return (round(127.32 - (pin - 2) * 1.27, 4), pi_even_y)

# TB6612 Left
tb1_top_y = 61.2075
tb1_bot_y = 76.4475
tb1_xs = [58.80, 61.34, 63.88, 66.42, 68.96, 71.50, 74.04, 76.58]
tb1 = {i+1: (tb1_xs[i], tb1_top_y) for i in range(8)}
tb1.update({i+9: (tb1_xs[i], tb1_bot_y) for i in range(8)})

# TB6612 Right
tb2_top_y = 61.2075
tb2_bot_y = 76.4475
tb2_xs = [131.80, 134.34, 136.88, 139.42, 141.96, 144.50, 147.04, 149.58]
tb2 = {i+1: (tb2_xs[i], tb2_top_y) for i in range(8)}
tb2.update({i+9: (tb2_xs[i], tb2_bot_y) for i in range(8)})

# Motors
m1 = {1: (66.408, 53.4005), 2: (68.948, 53.4005)}
m2 = {1: (75.53, 53.4425), 2: (78.07, 53.4425)}
m3 = {1: (138.53, 53.9425), 2: (141.07, 53.9425)}
m4 = {1: (149.53, 53.9425), 2: (152.07, 53.9425)}

# Sensors
tcrt = {1: (109.54, 50.4425), 2: (107.00, 50.4425), 3: (104.46, 50.4425), 4: (101.92, 50.4425), 5: (99.38, 50.4425)}
us1 = {1: (86.38, 50.4425), 2: (88.92, 50.4425), 3: (91.46, 50.4425), 4: (94.00, 50.4425)}
us2 = {1: (114.6059, 50.5138), 2: (117.1459, 50.5138), 3: (119.6859, 50.5138), 4: (122.2259, 50.5138)}

r1 = {1: (89.22, 65.9425), 2: (96.84, 65.9425)}
r2 = {1: (96.80, 72.4425), 2: (89.18, 72.4425)}
r3 = {1: (117.12, 61.4360), 2: (124.7449, 61.4360)}
r4 = {1: (117.16, 65.4452), 2: (124.78, 65.4452)}

oled = {1: (152.12, 96.50), 2: (149.58, 96.50), 3: (147.04, 96.50), 4: (144.50, 96.50)}

# Build all track paths
paths = []

def add(net, pts, width=0.6):
    for i in range(len(pts)-1):
        paths.append({
            'net': net,
            'p1': (round(pts[i][0], 4), round(pts[i][1], 4)),
            'p2': (round(pts[i+1][0], 4), round(pts[i+1][1], 4)),
            'width': width
        })

# 1. TB6612 LEFT Internal Arches
add("/AIN1_L", [tb1[3], (63.88, 64.5), (68.96, 64.5), tb1[5]])
add("/AIN2_L", [tb1[2], (61.34, 66.5), (71.50, 66.5), tb1[6]])
add("/PWMA_L", [tb1[1], (58.80, 68.5), (74.04, 68.5), tb1[7]])

# Left GND pins
add("GND", [tb1[8], tb1[16]])
add("GND", [tb1[11], (63.88, 73.0), (76.58, 73.0)])

# Left Control to Pi4
add("/PWMA_L", [tb1[7], (74.04, 59.0), (86.68, 59.0), pi_odd(33)])
add("/AIN2_L", [tb1[6], (71.50, 58.0), (84.14, 58.0), pi_odd(35)])
add("/AIN1_L", [tb1[5], (68.96, 57.0), (81.60, 57.0), pi_odd(37)])

# 2. TB6612 LEFT Motors
add("/M1_A", [tb1[12], (66.42, 78.5), (56.0, 78.5), (56.0, 53.4005), m1[1]], width=0.8)
add("/M1_B", [tb1[13], (68.96, 80.0), (54.0, 80.0), (54.0, 51.50), (68.948, 51.50), m1[2]], width=0.8)
add("/M2_B", [tb1[14], (71.50, 78.5), (79.5, 78.5), (79.5, 53.4425), m2[1]], width=0.8)
add("/M2_A", [tb1[15], (74.04, 80.0), (81.0, 80.0), (81.0, 51.50), (78.07, 51.50), m2[2]], width=0.8)

# 3. TB6612 RIGHT Internal Arches
add("/AIN1_R", [tb2[3], (136.88, 64.5), (141.96, 64.5), tb2[5]])
add("/AIN2_R", [tb2[2], (134.34, 66.5), (144.50, 66.5), tb2[6]])
add("/PWMA_R", [tb2[1], (131.80, 68.5), (147.04, 68.5), tb2[7]])

# Right GND pins
add("GND", [tb2[8], tb2[16]])
add("GND", [tb2[11], (136.88, 73.0), (149.58, 73.0)])

# Right Control to Pi4 (routing below R4)
add("/PWMA_R", [tb2[1], (131.80, 70.0), (124.78, 70.0), pi_odd(3)])
add("/AIN2_R", [tb2[2], (134.34, 71.5), (122.24, 71.5), pi_odd(5)])
add("/AIN1_R", [tb2[3], (136.88, 73.0), (119.70, 73.0), pi_odd(7)])

# 4. TB6612 RIGHT Motors
add("/M3_A", [tb2[12], (139.42, 78.5), (138.53, 78.5), m3[1]], width=0.8)
add("/M3_B", [tb2[13], (141.96, 80.0), (141.07, 80.0), m3[2]], width=0.8)
add("/M4_B", [tb2[14], (144.50, 78.5), (154.5, 78.5), (154.5, 51.50), (149.53, 51.50), m4[1]], width=0.8)
add("/M4_A", [tb2[15], (147.04, 80.0), (156.5, 80.0), (156.5, 53.9425), m4[2]], width=0.8)

# 5. TCRT5000 (Parallel straight down)
add("/LINE_R", [tcrt[5], pi_odd(23)])
add("/LINE_C", [tcrt[4], pi_odd(21)])
add("/LINE_L", [tcrt[3], pi_odd(19)])
add("/+3V3_LOGIC", [tcrt[2], pi_odd(17)])

# 6. Ultrasonics & Resistors
# Left
add("/TRIG_L", [us1[2], (88.92, 53.0), (88.0, 53.0), (88.0, 91.0), (89.22, 91.0), pi_odd(31)])
add("Net-(U_US1-ECHO)", [us1[3], (91.46, 63.0), (89.22, 63.0), r1[1]])
add("/ECHO_L", [r1[2], (96.84, 69.0), (96.80, 69.0), r2[1]])
add("/ECHO_L", [r2[1], (96.80, 75.0), (91.76, 75.0), pi_odd(29)])
add("GND", [r2[2], (89.18, 70.0), (94.0, 70.0), us1[4]])

# Right
add("/TRIG_R", [us2[2], (117.1459, 53.0), (109.54, 53.0), pi_odd(15)])
add("Net-(U_US2-ECHO)", [us2[3], (119.6859, 55.0), (117.12, 55.0), r3[1]])
add("/ECHO_R", [r3[2], (124.7449, 63.5), (124.78, 63.5), r4[2]])
add("/ECHO_R", [r4[2], (124.78, 68.0), (112.08, 68.0), pi_odd(13)])
add("GND", [r4[1], pi_odd(9)])

# Top Ground Rail connecting sensors at Y=46.50
add("GND", [tb1[8], (76.58, 46.50), (94.0, 46.50), us1[4]])
add("GND", [(94.0, 46.50), (109.54, 46.50), tcrt[1]])
add("GND", [(109.54, 46.50), (122.2259, 46.50), us2[4]])
add("GND", [(122.2259, 46.50), (149.58, 46.50), tb2[8]])

# 7. Ground Trunk along Y=101.50
trunk_gnd_y = 101.50
add("GND", [pi_odd(39), (79.06, trunk_gnd_y)])
add("GND", [pi_even(34), (86.68, trunk_gnd_y)])
add("GND", [pi_even(30), (91.76, trunk_gnd_y)])
add("GND", [pi_odd(25), (96.84, trunk_gnd_y)])
add("GND", [pi_even(20), (104.46, trunk_gnd_y)])
add("GND", [pi_even(14), (112.08, trunk_gnd_y)])
add("GND", [pi_even(6), (122.24, trunk_gnd_y)])
add("GND", [(76.58, trunk_gnd_y), (149.58, trunk_gnd_y)], width=1.2)

# Connect Left & Right TB6612 Pad 16 down to GND trunk
add("GND", [tb1[16], (76.58, trunk_gnd_y)])
add("GND", [tb2[16], (149.58, trunk_gnd_y)])
add("GND", [oled[2], (149.58, trunk_gnd_y)])

# 8. +5V_PWR Bus
trunk_5v_y = 104.50
add("/+5V_PWR", [pi_even(4), pi_even(2)], width=1.2)
add("/+5V_PWR", [pi_even(2), (127.32, trunk_5v_y), (51.50, trunk_5v_y), (51.50, 44.00), (86.38, 44.00), us1[1]], width=1.2)
add("/+5V_PWR", [(86.38, 44.00), (114.6059, 44.00), us2[1]], width=1.2)
add("/+5V_PWR", [tb1[10], (61.34, trunk_5v_y)], width=1.0)
add("/+5V_PWR", [tb2[10], (134.34, 82.0), (158.0, 82.0), (158.0, trunk_5v_y), (127.32, trunk_5v_y)], width=1.0)

# 9. Top Wire Jumpers tracks
# JMP1: SDA
add("/I2C_SDA", [pi_odd(27), (94.30, 87.00)])
add("/I2C_SDA", [(144.50, 87.00), oled[4]])

# JMP2: SCL
add("/I2C_SCL", [pi_even(28), (94.30, 99.00)])
add("/I2C_SCL", [(147.04, 99.00), oled[3]])

# JMP3: 3V3
add("/+3V3_LOGIC", [pi_odd(17), (107.00, 84.00)])
add("/+3V3_LOGIC", [(152.12, 84.00), oled[1]])

# JMP4: STBY_L
add("/STBY_L", [tb1[4], (66.42, 63.00)])
add("/STBY_L", [(81.60, 84.00), (81.60, 91.0), (78.0, 91.0), (78.0, 98.0), (81.60, 98.0), pi_even(38)])

# JMP5: STBY_R
add("/STBY_R", [tb2[4], (139.42, 63.00)])
add("/STBY_R", [(114.62, 85.00), pi_odd(11)])

# JMP6: VM_MOTOR
add("/VM_MOTOR", [tb1[9], (58.80, 81.00)], width=1.2)
add("/VM_MOTOR", [tb2[9], (131.80, 81.00)], width=1.2)

print(f"Total track segments: {len(paths)}")

# Check for intersections between tracks of different nets
conflicts = 0
for i in range(len(paths)):
    for j in range(i+1, len(paths)):
        s1 = paths[i]
        s2 = paths[j]
        if s1['net'] != s2['net']:
            if segments_intersect(s1['p1'], s1['p2'], s2['p1'], s2['p2']):
                print(f"CONFLICT between {s1['net']} ({s1['p1']}->{s1['p2']}) and {s2['net']} ({s2['p1']}->{s2['p2']})")
                conflicts += 1

print(f"Total intersection conflicts: {conflicts}")
