import math
import os
import re
from load_footprints import fps

components = [
    # Ref, Val, FP, X, Y, Rot
    ('BT1', 'BAT_3S2P_11.1V', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 52.00, 42.00, 0),
    ('SW1', 'SW_MAIN_10A', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 52.00, 56.00, 0),
    ('F1', '7.5A_Blade', 'Fuseholder_Blade_Mini_Keystone_3568', 52.00, 70.00, 0),
    ('U1', 'XL4015_Buck_5A', 'TerminalBlock_Phoenix_MKDS-1,5-4-5.08', 52.00, 88.00, 0),
    ('C1', '470uF_25V', 'CP_Radial_D8.0mm_P3.50mm', 56.00, 52.00, 0),
    ('J_M1', 'MOTOR_FL', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 68.00, 45.00, 0),
    ('J_M2', 'MOTOR_RL', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 77.00, 45.00, 0),
    ('U_TB1', 'TB6612_Left', 'Module_TB6612FNG_Breakout', 68.00, 68.00, 270),
    ('U_US1', 'HC_SR04_Left', 'Sensor_HC_SR04', 92.00, 45.00, 0),
    ('R1', '1k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 92.00, 58.00, 0),
    ('R2', '2k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 92.00, 66.00, 0),
    ('U_LINE', 'TCRT5000_3CH', 'Sensor_Line_TCRT5000_3CH', 106.00, 45.00, 180),
    ('U_US2', 'HC_SR04_Right', 'Sensor_HC_SR04', 120.00, 45.00, 0),
    ('R3', '1k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 120.00, 58.00, 0),
    ('R4', '2k', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 120.00, 66.00, 0),
    ('C2', '470uF_25V', 'CP_Radial_D8.0mm_P3.50mm', 133.00, 52.00, 0),
    ('J_M3', 'MOTOR_FR', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 140.00, 45.00, 0),
    ('J_M4', 'MOTOR_RR', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08', 149.00, 45.00, 0),
    ('U_TB2', 'TB6612_Right', 'Module_TB6612FNG_Breakout', 140.00, 68.00, 270),
    ('U_PI4', 'Raspberry_Pi_4_40Pin', 'PinSocket_2x20_P2.54mm_Vertical', 103.19, 94.83, 0),
    ('C3', '470uF_10V', 'CP_Radial_D6.3mm_P2.50mm', 126.00, 102.50, 0),
    ('C4', '100nF', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 119.00, 102.50, 0),
    ('J_OLED', 'OLED_1.3_I2C', 'Sensor_OLED_1.3', 145.00, 95.00, 0),
    ('R_JMP1', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 131.00, 84.00, 90),
    ('R_JMP2', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 136.00, 84.00, 90),
    ('R_JMP3', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 141.00, 84.00, 90),
    ('R_JMP4', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 114.00, 78.00, 0),
    ('R_JMP5', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 122.00, 78.00, 0),
    ('R_JMP6', '0R', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal', 130.00, 78.00, 0)
]

def get_world(x0, y0, rot_deg, lx, ly):
    rad = math.radians(rot_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    wx = x0 + lx * cos_a - ly * sin_a
    wy = y0 + lx * sin_a + ly * cos_a
    return round(wx, 4), round(wy, 4)

world_pads = {}
for ref, val, fp_name, x0, y0, rot in components:
    p_dict = fps[fp_name]
    world_pads[ref] = {}
    for p_num, p in p_dict.items():
        wx, wy = get_world(x0, y0, rot, p['lx'], p['ly'])
        world_pads[ref][p_num] = {
            'x': wx, 'y': wy,
            'sx': p['sx'], 'sy': p['sy'],
            'drill': p['drill']
        }

print(f"Total placed components: {len(world_pads)}")
for ref in ['BT1', 'U1', 'U_TB1', 'U_PI4', 'J_OLED', 'R_JMP1']:
    print(f"\n{ref}:")
    for p_num, p in sorted(world_pads[ref].items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
        print(f"  Pad {p_num:2}: ({p['x']:6.2f}, {p['y']:6.2f})")

