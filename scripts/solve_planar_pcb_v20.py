import math

# Pad positions
from solve_planar_pcb_v3 import (
    pi_odd, pi_even, tb1, tb2, m1, m2, m3, m4,
    tcrt, us1, us2, r1, r2, r3, r4, oled
)

r3_pad1_us2_echo = (124.7449, 61.4360) # Pad 1: Net-(U_US2-ECHO)
r3_pad2_echo_r = (117.1249, 61.4360)   # Pad 2: /ECHO_R
r4_pad1_echo_r = (117.1600, 65.4452)   # Pad 1: /ECHO_R
r4_pad2_gnd = (124.7800, 65.4452)      # Pad 2: GND

def chamfer_path(pts, d=1.5):
    """
    Replaces every 90-degree corner in pts with a 45-degree chamfer.
    """
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
        if abs(dot) < 0.25:
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

def build_v20_routing():
    paths.clear()

    # ==========================================================================
    # 1. TB6612 LEFT INTERNAL ARCHES (Inputs A & B bridged)
    # ==========================================================================
    add_chamfered("/AIN1_L", [tb1[3], (63.88, 64.5), (68.96, 64.5), tb1[5]], width=1.0, d=1.0)
    add_chamfered("/AIN2_L", [tb1[2], (61.34, 66.5), (71.50, 66.5), tb1[6]], width=1.0, d=1.0)
    add_chamfered("/PWMA_L", [tb1[1], (58.80, 68.5), (74.04, 68.5), tb1[7]], width=1.0, d=1.0)
    add_raw("GND", [tb1[8], tb1[16]], width=1.4)
    add_chamfered("GND", [tb1[11], (63.88, 73.0), (76.58, 73.0)], width=1.4, d=1.0)

    # ==========================================================================
    # 2. TB6612 LEFT MOTORS (Run up West channel X in [52.3, 56.8], around TB6612)
    # ==========================================================================
    add_chamfered("/M1_A", [tb1[12], (66.42, 79.5), (56.8, 79.5), (56.8, 53.4005), m1[1]], width=1.0, d=1.5)
    add_chamfered("/M1_B", [tb1[13], (68.96, 81.0), (55.3, 81.0), (55.3, 51.00), (68.948, 51.00), m1[2]], width=1.0, d=1.5)
    add_chamfered("/M2_B", [tb1[14], (71.50, 82.5), (53.8, 82.5), (53.8, 49.00), (75.53, 49.00), m2[1]], width=1.0, d=1.5)
    add_chamfered("/M2_A", [tb1[15], (74.04, 84.0), (52.3, 84.0), (52.3, 47.00), (78.07, 47.00), m2[2]], width=1.0, d=1.5)

    # ==========================================================================
    # 3. TB6612 LEFT CONTROL TO PI 4 (North concentric nested arches, 45° bends)
    # ==========================================================================
    add_chamfered("/PWMA_L", [tb1[7], (74.04, 59.0), (81.60, 59.0), pi_odd(37)], width=1.0, d=1.5)
    add_chamfered("/AIN2_L", [tb1[6], (71.50, 57.5), (84.14, 57.5), pi_odd(35)], width=1.0, d=1.5)
    add_chamfered("/AIN1_L", [tb1[5], (68.96, 56.0), (86.68, 56.0), pi_odd(33)], width=1.0, d=1.5)

    # ==========================================================================
    # 4. TB6612 RIGHT INTERNAL ARCHES (Inputs A & B bridged)
    # ==========================================================================
    add_chamfered("/AIN1_R", [tb2[3], (136.88, 64.5), (141.96, 64.5), tb2[5]], width=1.0, d=1.0)
    add_chamfered("/AIN2_R", [tb2[2], (134.34, 66.5), (144.50, 66.5), tb2[6]], width=1.0, d=1.0)
    add_chamfered("/PWMA_R", [tb2[1], (131.80, 68.5), (147.04, 68.5), tb2[7]], width=1.0, d=1.0)
    add_raw("GND", [tb2[8], tb2[16]], width=1.4)
    add_chamfered("GND", [tb2[11], (136.88, 73.0), (149.58, 73.0)], width=1.4, d=1.0)

    # ==========================================================================
    # 5. TB6612 RIGHT MOTORS (Run up East channel X in [152, 157.5], 45° bends)
    # ==========================================================================
    add_chamfered("/M4_A", [tb2[15], (147.04, 78.5), (152.07, 78.5), m4[2]], width=1.0, d=1.5)
    add_chamfered("/M4_B", [tb2[14], (144.50, 80.0), (154.5, 80.0), (154.5, 51.50), (149.53, 51.50), m4[1]], width=1.0, d=1.5)
    add_chamfered("/M3_B", [tb2[13], (141.96, 81.5), (156.0, 81.5), (156.0, 49.50), (141.07, 49.50), m3[2]], width=1.0, d=1.5)
    add_chamfered("/M3_A", [tb2[12], (139.42, 83.0), (157.5, 83.0), (157.5, 48.00), (138.53, 48.00), m3[1]], width=1.0, d=1.5)

    # ==========================================================================
    # 6. TB6612 RIGHT CONTROL TO PI 4 (Via Clean Top Wire Jumpers)
    # ==========================================================================
    # J14: PWM-R from tb2[1] via at (131.80, 57.0) to via at (124.78, 88.0) -> Pin 3
    add_raw("/PWMA_R", [tb2[1], (131.80, 57.00)], width=1.0)
    add_raw("/PWMA_R", [(124.78, 88.00), pi_odd(3)], width=1.0)

    # J15: IN2-R from tb2[2] via at (134.34, 57.0) to via at (122.24, 86.0) -> Pin 5
    add_raw("/AIN2_R", [tb2[2], (134.34, 57.00)], width=1.0)
    add_raw("/AIN2_R", [(122.24, 86.00), pi_odd(5)], width=1.0)

    # J16: IN1-R from tb2[3] via at (136.88, 57.0) to via at (119.70, 84.0) -> Pin 7
    add_raw("/AIN1_R", [tb2[3], (136.88, 57.00)], width=1.0)
    add_raw("/AIN1_R", [(119.70, 84.00), pi_odd(7)], width=1.0)

    # ==========================================================================
    # 7. TCRT5000 SENSORS (Parallel straight vertical tracks, width 1.0mm)
    # ==========================================================================
    add_raw("/LINE_R", [tcrt[5], pi_odd(23)], width=1.0)
    add_raw("/LINE_C", [tcrt[4], pi_odd(21)], width=1.0)
    add_raw("/LINE_L", [tcrt[3], pi_odd(19)], width=1.0)
    add_raw("/+3V3_LOGIC", [tcrt[2], pi_odd(17)], width=1.0)

    # ==========================================================================
    # 8. ULTRASONIC SENSORS & VOLTAGE DIVIDERS
    # ==========================================================================
    # Left Ultrasonic:
    # J17: TRIG-L via jumper from us1[2] via at (88.92, 53.50) to via at (89.22, 90.00) -> Pin 31
    add_raw("/TRIG_L", [us1[2], (88.92, 53.50)], width=1.0)
    add_raw("/TRIG_L", [(89.22, 90.00), pi_odd(31)], width=1.0)

    # Echo divider Left:
    add_chamfered("Net-(U_US1-ECHO)", [us1[3], (91.46, 62.0), (89.22, 62.0), r1[1]], width=1.0, d=1.0)
    add_raw("/ECHO_L", [r1[2], (96.84, 69.00), r2[1]], width=1.0)
    add_chamfered("/ECHO_L", [r2[1], (96.80, 77.0), (91.76, 77.0), pi_odd(29)], width=1.0, d=1.5)
    
    # Left top GND:
    add_chamfered("GND", [r2[2], (89.18, 74.00), (94.00, 74.00), (94.00, 50.4425), us1[4]], width=1.4, d=1.0)
    add_chamfered("GND", [us1[4], (94.00, 47.00), (109.54, 47.00), tcrt[1]], width=1.4, d=1.5)

    # Top GND jumper J12 from (94.00, 62.00) to (91.76, 99.00) on bottom trunk:
    add_raw("GND", [(94.00, 62.00), (94.00, 62.00)], width=1.4)
    add_raw("GND", [(91.76, 99.00), pi_even(30)], width=1.4)

    # Right Ultrasonic:
    # TRIG_R goes planar to Pin 15 (width 1.0mm, 45° bend):
    add_chamfered("/TRIG_R", [us2[2], (117.1459, 53.5), (109.54, 53.5), pi_odd(15)], width=1.0, d=1.5)
    
    # Echo divider Right:
    add_chamfered("Net-(U_US2-ECHO)", [us2[3], (119.6859, 54.0), (124.7449, 54.0), r3_pad1_us2_echo], width=1.0, d=1.0)
    add_raw("/ECHO_R", [r3_pad2_echo_r, r4_pad1_echo_r, (117.1600, 68.00)], width=1.0)
    # J7: ECHO-R from (117.16, 68.00) to (112.08, 88.00) -> Pin 13:
    add_raw("/ECHO_R", [(112.08, 88.00), pi_odd(13)], width=1.0)

    # Right top GND: Connect US2 Pad 4 to R4 Pad 2 cleanly on B.Cu!
    add_chamfered("GND", [us2[4], (127.00, 50.5138), (127.00, 65.4452), r4_pad2_gnd], width=1.4, d=1.5)
    
    # J13: GND-US2 from R4 Pad 2 at (127.00, 67.50) to TB6612 Right GND at (136.88, 73.00):
    add_raw("GND", [(127.00, 65.4452), (127.00, 67.50)], width=1.4)
    add_raw("GND", [(136.88, 73.00), tb2[11]], width=1.4)

    # ==========================================================================
    # 9. GROUND TRUNK ALONG Y = 101.50 (Power width = 1.4mm)
    # ==========================================================================
    trunk_gnd_y = 101.50
    add_chamfered("GND", [pi_odd(39), (77.00, 93.5575), (77.00, trunk_gnd_y), (122.24, trunk_gnd_y), pi_even(6)], width=1.4, d=1.5)
    add_raw("GND", [pi_even(34), (86.68, trunk_gnd_y)], width=1.4)
    add_raw("GND", [pi_even(30), (91.76, trunk_gnd_y)], width=1.4)
    
    # Pin 25 via jumper J9 over Pi socket:
    add_raw("GND", [pi_odd(25), (96.84, 89.00)], width=1.4)
    add_raw("GND", [(96.84, 99.00), (96.84, trunk_gnd_y)], width=1.4)
    
    add_raw("GND", [pi_even(20), (104.46, trunk_gnd_y)], width=1.4)
    add_raw("GND", [pi_even(14), (112.08, trunk_gnd_y)], width=1.4)

    # Pin 40 grounded locally:
    add_raw("GND", [pi_even(40), (79.06, trunk_gnd_y)], width=1.4)

    # J8: GND-R jumper to TB6612 Right Pad 16:
    add_raw("GND", [tb2[16], (149.58, 69.00)], width=1.4)
    add_raw("GND", [(149.58, 90.00), oled[2]], width=1.4)

    # ==========================================================================
    # 10. +5V_PWR BUS (Power width = 1.4mm, 45° bends everywhere)
    # ==========================================================================
    bus_5v_y = 105.00
    west_5v_x = 50.30
    top_5v_y = 43.50

    add_raw("/+5V_PWR", [pi_even(4), pi_even(2)], width=1.4)
    add_chamfered("/+5V_PWR", [
        pi_even(2),
        (127.32, bus_5v_y),
        (west_5v_x, bus_5v_y),
        (west_5v_x, top_5v_y),
        (114.6059, top_5v_y),
        us2[1]
    ], width=1.4, d=2.0)
    
    add_raw("/+5V_PWR", [(86.38, top_5v_y), us1[1]], width=1.4)

    # J10: +5V-L to TB6612 Left VCC:
    add_raw("/+5V_PWR", [(61.34, 43.50), (61.34, 43.50)], width=1.4)
    add_raw("/+5V_PWR", [(61.34, 74.00), tb1[10]], width=1.4)

    # J11: +5V-R to TB6612 Right VCC:
    add_raw("/+5V_PWR", [pi_even(2), (127.32, 99.00)], width=1.4)
    add_raw("/+5V_PWR", [(134.34, 74.00), tb2[10]], width=1.4)

    # ==========================================================================
    # 11. MOTOR POWER (VM_MOTOR, Power width = 1.4mm)
    # ==========================================================================
    add_raw("/VM_MOTOR", [tb1[9], (58.80, 74.00)], width=1.4)
    add_raw("/VM_MOTOR", [(131.80, 74.00), tb2[9]], width=1.4)

    # ==========================================================================
    # 12. I2C BUS (OLED & EXPANSION, Signal width = 1.0mm)
    # ==========================================================================
    # J1: SDA
    add_raw("/I2C_SDA", [pi_odd(27), (94.30, 87.00)], width=1.0)
    add_raw("/I2C_SDA", [(144.50, 87.00), oled[4]], width=1.0)

    # J2: SCL
    add_raw("/I2C_SCL", [pi_even(28), (94.30, 99.00)], width=1.0)
    add_raw("/I2C_SCL", [(147.04, 99.00), oled[3]], width=1.0)

    # J3: 3V3
    add_raw("/+3V3_LOGIC", [pi_odd(17), (107.00, 84.00)], width=1.0)
    add_raw("/+3V3_LOGIC", [(152.12, 88.00), oled[1]], width=1.0)

    # ==========================================================================
    # 13. MOTOR STANDBY (Signal width = 1.0mm)
    # ==========================================================================
    # J4: STBY-L
    add_raw("/STBY_L", [tb1[4], (66.42, 58.00)], width=1.0)
    add_raw("/STBY_L", [(81.60, 99.00), pi_even(38)], width=1.0)

    # J5: STBY-R
    add_raw("/STBY_R", [tb2[4], (139.42, 58.00)], width=1.0)
    add_raw("/STBY_R", [(114.62, 85.00), pi_odd(11)], width=1.0)

build_v20_routing()
