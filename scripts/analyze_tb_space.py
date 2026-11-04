# Check routing space around TB6612 LEFT and RIGHT

# TB6612 LEFT:
# Row 2 (Pads 9-16) at Y = 76.45:
# Pad 9 (VM): X = 58.80
# Pad 10 (VCC): X = 61.34
# Pad 11 (GND): X = 63.88
# Pad 12 (AO1): X = 66.42
# Pad 13 (AO2): X = 68.96
# Pad 14 (BO2): X = 71.50
# Pad 15 (BO1): X = 74.04
# Pad 16 (GND): X = 76.58

# Row 1 (Pads 1-8) at Y = 61.21:
# Pad 1 (PWMA): X = 58.80
# Pad 2 (AIN2): X = 61.34
# Pad 3 (AIN1): X = 63.88
# Pad 4 (STBY): X = 66.42
# Pad 5 (BIN1): X = 68.96
# Pad 6 (BIN2): X = 71.50
# Pad 7 (PWMB): X = 74.04
# Pad 8 (GND): X = 76.58

# Space inside socket:
# X between 58.80 and 76.58 (17.78 mm wide)
# Y between 61.21 and 76.45 (15.24 mm high)
# Between row 1 and row 2, the clearance between pad edges is:
# 15.24 - 2.0 = 13.24 mm!
print(f"Internal socket height: 13.24 mm")
print(f"Internal socket width: 17.78 mm")

