import json
with open('scripts/test_routes_clean.py', 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.splitlines():
    if 'Net-(U_PI4-GPIO16_AIN1_R)' in line or 'I2C_SDA' in line:
        print(line)
