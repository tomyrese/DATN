with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

import re
# Remove (net_class ...) block
text = re.sub(r'\(net_class\s+"Default"[\s\S]*?\n\t\)', '', text)

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Removed net_class block.")

