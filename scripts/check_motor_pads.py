import json
with open('scripts/world_pads_v2.json') as f:
    pads = json.load(f)

for comp in ['MOTOR1', 'MOTOR2', 'MOTOR3', 'MOTOR4']:
    print(comp, pads[comp])
