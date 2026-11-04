with open('Pi4_Robot_Carrier_1Layer.kicad_sch.bak', 'r', encoding='utf-8') as f:
    text = f.read()

import re
labels = re.findall(r'\(label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text)
for name, x, y in labels:
    if any(k in name.upper() for k in ['OLED', 'I2C', 'SDA', 'SCL', 'MOTOR', 'PWM', 'TRIG', 'ECHO', 'LINE']):
        print(f'{name:25s} at ({x}, {y})')

