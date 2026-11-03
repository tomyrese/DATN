# Let's inspect all pad coordinates and clearances
import json

with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    wp = json.load(f)

print("Check Left Motor connectors:")
print("MOTOR1:", wp['MOTOR1'])
print("MOTOR2:", wp['MOTOR2'])

print("\nCheck Right Motor connectors:")
print("MOTOR3:", wp['MOTOR3'])
print("MOTOR4:", wp['MOTOR4'])

print("\nCheck Left TB6612:")
for p in range(1, 17):
    print(f"LEFT {p}: {wp['LEFT'][str(p)]}")

print("\nCheck Right TB6612:")
for p in range(1, 17):
    print(f"RIGHT {p}: {wp['RIGHT'][str(p)]}")
