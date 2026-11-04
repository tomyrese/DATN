for name in ['CP_Radial_D6.3mm_P2.50mm.kicad_mod', 'C_Disc_D5.0mm_W2.5mm_P5.00mm.kicad_mod', 'Sensor_OLED_1.3.kicad_mod']:
    with open('libraries/robot_electronics.pretty/' + name, 'r', encoding='utf-8') as f:
        print(f"=== {name} ===")
        print(f.read())

