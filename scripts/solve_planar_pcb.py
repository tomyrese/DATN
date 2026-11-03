import json

with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    wp = json.load(f)

def pad_pt(ref, pad_num):
    p = wp[ref][str(pad_num)]
    return (round(p['x'], 4), round(p['y'], 4))

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    eps = 1e-3
    for p1 in [A, B]:
        for p2 in [C, D]:
            if abs(p1[0]-p2[0]) < eps and abs(p1[1]-p2[1]) < eps:
                return False
    if max(A[0], B[0]) < min(C[0], D[0]) - eps or max(C[0], D[0]) < min(A[0], B[0]) - eps:
        return False
    if max(A[1], B[1]) < min(C[1], D[1]) - eps or max(C[1], D[1]) < min(A[1], B[1]) - eps:
        return False
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

paths = [] # list of (net, (x1, y1), (x2, y2), width)

def add_line(net, p1, p2, width=0.6):
    paths.append((net, p1, p2, width))

def add_path(net, pts, width=0.6):
    for i in range(len(pts)-1):
        add_line(net, pts[i], pts[i+1], width)

# Left TB6612 Pads
p_tb1_1 = pad_pt("LEFT", 1)
p_tb1_2 = pad_pt("LEFT", 2)
p_tb1_3 = pad_pt("LEFT", 3)
p_tb1_4 = pad_pt("LEFT", 4)
p_tb1_5 = pad_pt("LEFT", 5)
p_tb1_6 = pad_pt("LEFT", 6)
p_tb1_7 = pad_pt("LEFT", 7)
p_tb1_8 = pad_pt("LEFT", 8)
p_tb1_9 = pad_pt("LEFT", 9)
p_tb1_10 = pad_pt("LEFT", 10)
p_tb1_11 = pad_pt("LEFT", 11)
p_tb1_12 = pad_pt("LEFT", 12)
p_tb1_13 = pad_pt("LEFT", 13)
p_tb1_14 = pad_pt("LEFT", 14)
p_tb1_15 = pad_pt("LEFT", 15)
p_tb1_16 = pad_pt("LEFT", 16)

# Right TB6612 Pads
p_tb2_1 = pad_pt("RIGHT", 1)
p_tb2_2 = pad_pt("RIGHT", 2)
p_tb2_3 = pad_pt("RIGHT", 3)
p_tb2_4 = pad_pt("RIGHT", 4)
p_tb2_5 = pad_pt("RIGHT", 5)
p_tb2_6 = pad_pt("RIGHT", 6)
p_tb2_7 = pad_pt("RIGHT", 7)
p_tb2_8 = pad_pt("RIGHT", 8)
p_tb2_9 = pad_pt("RIGHT", 9)
p_tb2_10 = pad_pt("RIGHT", 10)
p_tb2_11 = pad_pt("RIGHT", 11)
p_tb2_12 = pad_pt("RIGHT", 12)
p_tb2_13 = pad_pt("RIGHT", 13)
p_tb2_14 = pad_pt("RIGHT", 14)
p_tb2_15 = pad_pt("RIGHT", 15)
p_tb2_16 = pad_pt("RIGHT", 16)

# Motor Pads
p_m1_1 = pad_pt("MOTOR1", 1)
p_m1_2 = pad_pt("MOTOR1", 2)
p_m2_1 = pad_pt("MOTOR2", 1)
p_m2_2 = pad_pt("MOTOR2", 2)
p_m3_1 = pad_pt("MOTOR3", 1)
p_m3_2 = pad_pt("MOTOR3", 2)
p_m4_1 = pad_pt("MOTOR4", 1)
p_m4_2 = pad_pt("MOTOR4", 2)

# Pi Pads
p_pi2 = pad_pt("Rasp_PI4", 2)
p_pi4 = pad_pt("Rasp_PI4", 4)
p_pi6 = pad_pt("Rasp_PI4", 6)
p_pi14 = pad_pt("Rasp_PI4", 14)
p_pi20 = pad_pt("Rasp_PI4", 20)
p_pi25 = pad_pt("Rasp_PI4", 25)
p_pi30 = pad_pt("Rasp_PI4", 30)
p_pi34 = pad_pt("Rasp_PI4", 34)
p_pi39 = pad_pt("Rasp_PI4", 39)

p_pi3 = pad_pt("Rasp_PI4", 3)
p_pi5 = pad_pt("Rasp_PI4", 5)
p_pi7 = pad_pt("Rasp_PI4", 7)
p_pi11 = pad_pt("Rasp_PI4", 11)
p_pi13 = pad_pt("Rasp_PI4", 13)
p_pi15 = pad_pt("Rasp_PI4", 15)
p_pi17 = pad_pt("Rasp_PI4", 17)
p_pi19 = pad_pt("Rasp_PI4", 19)
p_pi21 = pad_pt("Rasp_PI4", 21)
p_pi23 = pad_pt("Rasp_PI4", 23)
p_pi27 = pad_pt("Rasp_PI4", 27)
p_pi28 = pad_pt("Rasp_PI4", 28)
p_pi29 = pad_pt("Rasp_PI4", 29)
p_pi31 = pad_pt("Rasp_PI4", 31)
p_pi33 = pad_pt("Rasp_PI4", 33)
p_pi35 = pad_pt("Rasp_PI4", 35)
p_pi37 = pad_pt("Rasp_PI4", 37)
p_pi38 = pad_pt("Rasp_PI4", 38)

# Sensor Pads
p_tcrt_1 = pad_pt("TCRT5000", 1)
p_tcrt_2 = pad_pt("TCRT5000", 2)
p_tcrt_3 = pad_pt("TCRT5000", 3)
p_tcrt_4 = pad_pt("TCRT5000", 4)
p_tcrt_5 = pad_pt("TCRT5000", 5)

p_us1_1 = pad_pt("HC_SR04_1", 1)
p_us1_2 = pad_pt("HC_SR04_1", 2)
p_us1_3 = pad_pt("HC_SR04_1", 3)
p_us1_4 = pad_pt("HC_SR04_1", 4)
p_r1_1 = pad_pt("R1", 1)
p_r1_2 = pad_pt("R1", 2)
p_r2_1 = pad_pt("R2", 1)
p_r2_2 = pad_pt("R2", 2)

p_us2_1 = pad_pt("HC_SR04_2", 1)
p_us2_2 = pad_pt("HC_SR04_2", 2)
p_us2_3 = pad_pt("HC_SR04_2", 3)
p_us2_4 = pad_pt("HC_SR04_2", 4)
p_r3_1 = pad_pt("R3", 1)
p_r3_2 = pad_pt("R3", 2)
p_r4_1 = pad_pt("R4", 1)
p_r4_2 = pad_pt("R4", 2)

p_oled_1 = pad_pt("OLED", 1)
p_oled_2 = pad_pt("OLED", 2)
p_oled_3 = pad_pt("OLED", 3)
p_oled_4 = pad_pt("OLED", 4)

print("Pads loaded successfully.")
