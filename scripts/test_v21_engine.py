import math

def chamfer_path(pts, d=1.5):
    if len(pts) <= 2:
        return list(pts)
    result = [pts[0]]
    for i in range(1, len(pts) - 1):
        p_prev = pts[i - 1]
        p_curr = pts[i]
        p_next = pts[i + 1]
        dx1 = p_curr[0] - p_prev[0]
        dy1 = p_curr[1] - p_prev[1]
        len1 = math.hypot(dx1, dy1)
        dx2 = p_next[0] - p_curr[0]
        dy2 = p_next[1] - p_curr[1]
        len2 = math.hypot(dx2, dy2)
        if len1 < 1e-4 or len2 < 1e-4:
            continue
        ux1, uy1 = dx1 / len1, dy1 / len1
        ux2, uy2 = dx2 / len2, dy2 / len2
        dot = ux1 * ux2 + uy1 * uy2
        if abs(dot) < 0.25: # 90-degree corner
            actual_d = min(d, len1 * 0.40, len2 * 0.40)
            p_in = (round(p_curr[0] - ux1 * actual_d, 4), round(p_curr[1] - uy1 * actual_d, 4))
            p_out = (round(p_curr[0] + ux2 * actual_d, 4), round(p_curr[1] + uy2 * actual_d, 4))
            result.append(p_in)
            result.append(p_out)
        else:
            result.append(p_curr)
    result.append(pts[-1])
    return result

paths = []
def add_raw(net, pts, width=1.0):
    for i in range(len(pts) - 1):
        paths.append({
            'net': net,
            'p1': (round(pts[i][0], 4), round(pts[i][1], 4)),
            'p2': (round(pts[i+1][0], 4), round(pts[i+1][1], 4)),
            'width': width
        })

def add_chamfered(net, pts, width=1.0, d=1.5):
    c_pts = chamfer_path(pts, d=d)
    add_raw(net, c_pts, width=width)

# TB1
tb1_s = {
    1: (76.58, 76.45), 2: (74.04, 76.45), 3: (71.50, 76.45), 4: (68.96, 76.45),
    5: (66.42, 76.45), 6: (63.88, 76.45), 7: (61.34, 76.45), 8: (58.80, 76.45)
}
tb1_n = {
    9: (76.58, 61.21), 10: (74.04, 61.21), 11: (71.50, 61.21), 12: (68.96, 61.21),
    13: (66.42, 61.21), 14: (63.88, 61.21), 15: (61.34, 61.21), 16: (58.80, 61.21)
}

# TB2
tb2_s = {
    1: (149.58, 76.45), 2: (147.04, 76.45), 3: (144.50, 76.45), 4: (141.96, 76.45),
    5: (139.42, 76.45), 6: (136.88, 76.45), 7: (134.34, 76.45), 8: (131.80, 76.45)
}
tb2_n = {
    9: (149.58, 61.21), 10: (147.04, 61.21), 11: (144.50, 61.21), 12: (141.96, 61.21),
    13: (139.42, 61.21), 14: (136.88, 61.21), 15: (134.34, 61.21), 16: (131.80, 61.21)
}

def pi_odd(pin):
    idx = (39 - pin) // 2
    return (round(79.06 + idx * 2.54, 4), 93.5575)

def pi_even(pin):
    idx = (40 - pin) // 2
    return (round(79.06 + idx * 2.54, 4), 96.0975)

m1 = {1: (66.41, 53.40), 2: (68.95, 53.40)}
m2 = {1: (75.53, 53.44), 2: (78.07, 53.44)}
m3 = {1: (138.53, 53.94), 2: (141.07, 53.94)}
m4 = {1: (149.53, 53.94), 2: (152.07, 53.94)}

r1 = {1: (89.22, 65.94), 2: (96.84, 65.94)}
r2 = {1: (96.80, 72.44), 2: (89.18, 72.44)}
r3 = {1: (124.74, 61.44), 2: (117.12, 61.44)}
r4 = {1: (117.16, 65.45), 2: (124.78, 65.45)}

us1 = {1: (86.38, 50.44), 2: (88.92, 50.44), 3: (91.46, 50.44), 4: (94.00, 50.44)}
us2 = {1: (114.61, 50.51), 2: (117.15, 50.51), 3: (119.69, 50.51), 4: (122.23, 50.51)}
tcrt = {1: (109.54, 50.44), 2: (107.00, 50.44), 3: (104.46, 50.44), 4: (101.92, 50.44), 5: (99.38, 50.44)}
oled = {1: (152.12, 96.50), 2: (149.58, 96.50), 3: (147.04, 96.50), 4: (144.50, 96.50)}

def route_all():
    paths.clear()

    # 1. TB1 Arches
    add_chamfered("/AIN1_L", [tb1_s[3], (71.50, 71.0), (66.42, 71.0), tb1_s[5]], width=1.0, d=1.0)
    add_chamfered("/AIN2_L", [tb1_s[2], (74.04, 68.5), (63.88, 68.5), tb1_s[6]], width=1.0, d=1.0)
    add_chamfered("/PWMA_L", [tb1_s[1], (76.58, 66.0), (61.34, 66.0), tb1_s[7]], width=1.0, d=1.0)
    add_raw("GND", [tb1_s[8], tb1_n[16]], width=1.4)

    # 2. TB1 to Pi 4
    add_chamfered("/PWMA_L", [tb1_s[7], (61.34, 83.0), (81.60, 83.0), pi_odd(37)], width=1.0, d=1.5)
    add_chamfered("/AIN2_L", [tb1_s[6], (63.88, 85.5), (84.14, 85.5), pi_odd(35)], width=1.0, d=1.5)
    add_chamfered("/AIN1_L", [tb1_s[5], (66.42, 88.0), (86.68, 88.0), pi_odd(33)], width=1.0, d=1.5)
    
    # STBY_L: loops south around west side into Pin 38
    add_chamfered("/STBY_L", [tb1_s[4], (68.96, 98.50), (81.60, 98.50), pi_even(38)], width=1.0, d=1.5)

    # 3. TB1 Motors
    add_chamfered("/M1_A", [tb1_n[12], (68.96, 57.0), (66.41, 55.0), m1[1]], width=1.0, d=1.0)
    add_chamfered("/M1_B", [tb1_n[13], (66.42, 58.5), (55.00, 58.5), (55.00, 51.0), (68.95, 51.0), m1[2]], width=1.0, d=1.5)
    add_chamfered("/M2_B", [tb1_n[14], (63.88, 57.0), (75.53, 57.0), m2[1]], width=1.0, d=1.0)
    add_chamfered("/M2_A", [tb1_n[15], (61.34, 55.5), (78.07, 55.5), m2[2]], width=1.0, d=1.0)

    # 4. TB2 Arches
    add_chamfered("/AIN1_R", [tb2_s[3], (144.50, 71.0), (139.42, 71.0), tb2_s[5]], width=1.0, d=1.0)
    add_chamfered("/AIN2_R", [tb2_s[2], (147.04, 68.5), (136.88, 68.5), tb2_s[6]], width=1.0, d=1.0)
    add_chamfered("/PWMA_R", [tb2_s[1], (149.58, 66.0), (134.34, 66.0), tb2_s[7]], width=1.0, d=1.0)
    add_raw("GND", [tb2_s[8], tb2_n[16]], width=1.4)

    # 5. TB2 to Pi 4
    add_chamfered("/PWMA_R", [tb2_s[7], (134.34, 83.0), (124.78, 83.0), pi_odd(3)], width=1.0, d=1.5)
    add_chamfered("/AIN2_R", [tb2_s[6], (136.88, 85.5), (122.24, 85.5), pi_odd(5)], width=1.0, d=1.5)
    add_chamfered("/AIN1_R", [tb2_s[5], (139.42, 88.0), (119.70, 88.0), pi_odd(7)], width=1.0, d=1.5)
    add_chamfered("/STBY_R", [tb2_s[4], (141.96, 90.5), (114.62, 90.5), pi_odd(11)], width=1.0, d=1.5)

    # 6. TB2 Motors
    add_chamfered("/M3_A", [tb2_n[12], (141.96, 57.0), (138.53, 57.0), m3[1]], width=1.0, d=1.0)
    add_chamfered("/M3_B", [tb2_n[13], (139.42, 58.5), (130.00, 58.5), (130.00, 51.0), (141.07, 51.0), m3[2]], width=1.0, d=1.5)
    add_chamfered("/M4_B", [tb2_n[14], (136.88, 57.0), (149.53, 57.0), m4[1]], width=1.0, d=1.0)
    add_chamfered("/M4_A", [tb2_n[15], (134.34, 55.5), (152.07, 55.5), m4[2]], width=1.0, d=1.0)

    # 7. TCRT5000
    add_raw("/LINE_R", [tcrt[5], pi_odd(23)], width=1.0)
    add_raw("/LINE_C", [tcrt[4], pi_odd(21)], width=1.0)
    add_raw("/LINE_L", [tcrt[3], pi_odd(19)], width=1.0)
    add_raw("/+3V3_LOGIC", [tcrt[2], pi_odd(17)], width=1.0)

    # 8. Ultrasonics
    # TRIG_L
    add_chamfered("/TRIG_L", [us1[2], (88.92, 53.0), (89.22, 53.0), pi_odd(31)], width=1.0, d=1.5)
    # ECHO_L
    add_chamfered("Net-(U_US1-ECHO)", [us1[3], (91.46, 62.0), (89.22, 62.0), r1[1]], width=1.0, d=1.0)
    add_raw("/ECHO_L", [r1[2], (96.84, 69.0), r2[1]], width=1.0)
    add_chamfered("/ECHO_L", [r2[1], (96.80, 77.0), (91.76, 77.0), pi_odd(29)], width=1.0, d=1.5)

    # TRIG_R
    add_chamfered("/TRIG_R", [us2[2], (117.15, 53.5), (109.54, 53.5), pi_odd(15)], width=1.0, d=1.5)
    # ECHO_R
    add_chamfered("Net-(U_US2-ECHO)", [us2[3], (119.69, 54.0), (124.74, 54.0), r3[1]], width=1.0, d=1.0)
    add_raw("/ECHO_R", [r3[2], r4[1]], width=1.0)
    add_chamfered("/ECHO_R", [r4[1], (117.16, 70.0), (112.08, 70.0), pi_odd(13)], width=1.0, d=1.5)

    # 9. GND
    # Top ground
    add_chamfered("GND", [r2[2], (89.18, 74.0), (94.00, 74.0), us1[4]], width=1.4, d=1.0)
    add_chamfered("GND", [us1[4], (94.00, 47.0), (109.54, 47.0), tcrt[1]], width=1.4, d=1.5)
    add_chamfered("GND", [tcrt[1], (109.54, 47.0), (122.23, 47.0), us2[4]], width=1.4, d=1.5)
    add_chamfered("GND", [us2[4], (124.78, 50.51), r4[2]], width=1.4, d=1.0)
    add_chamfered("GND", [r4[2], (124.78, 72.0), (131.80, 72.0), tb2_s[8]], width=1.4, d=1.0)

    # North-to-South Highway (US1 Pad 4 to Pi Pin 25)
    add_chamfered("GND", [us1[4], (94.00, 85.0), (96.84, 88.0), pi_odd(25)], width=1.4, d=1.5)

    # Bottom Trunk Y = 101.50
    trunk_gnd_y = 101.50
    add_chamfered("GND", [tb1_s[8], (58.80, trunk_gnd_y), (77.00, trunk_gnd_y), (77.00, 93.56), pi_odd(39)], width=1.4, d=1.5)
    add_raw("GND", [pi_even(40), (79.06, trunk_gnd_y)], width=1.4)
    add_raw("GND", [pi_even(34), (86.68, trunk_gnd_y)], width=1.4)
    add_raw("GND", [pi_even(30), (91.76, trunk_gnd_y)], width=1.4)
    add_raw("GND", [pi_odd(25), (96.84, trunk_gnd_y)], width=1.4)
    add_raw("GND", [pi_even(20), (104.46, trunk_gnd_y)], width=1.4)
    add_raw("GND", [pi_even(14), (112.08, trunk_gnd_y)], width=1.4)
    add_raw("GND", [pi_even(6), (122.24, trunk_gnd_y)], width=1.4)
    add_chamfered("GND", [(77.00, trunk_gnd_y), (149.58, trunk_gnd_y), oled[2]], width=1.4, d=1.5)

    # 10. +5V_PWR
    bus_5v_y = 105.00
    west_5v_x = 51.00
    top_5v_y = 44.00
    add_raw("/+5V_PWR", [pi_even(4), pi_even(2)], width=1.4)
    add_chamfered("/+5V_PWR", [
        pi_even(2),
        (127.32, bus_5v_y),
        (west_5v_x, bus_5v_y),
        (west_5v_x, top_5v_y),
        (147.04, top_5v_y),
        tb2_n[10]
    ], width=1.4, d=2.0)
    add_chamfered("/+5V_PWR", [(74.04, top_5v_y), tb1_n[10]], width=1.4, d=1.0)
    add_chamfered("/+5V_PWR", [(86.38, top_5v_y), us1[1]], width=1.4, d=1.0)
    add_chamfered("/+5V_PWR", [(114.61, top_5v_y), us2[1]], width=1.4, d=1.0)

    # 11. VM_MOTOR
    top_vm_y = 41.50
    add_chamfered("/VM_MOTOR", [
        tb1_n[9],
        (76.58, top_vm_y),
        (149.58, top_vm_y),
        tb2_n[9]
    ], width=1.4, d=1.5)

route_all()
print(f"Total track segments routed: {len(paths)}")

