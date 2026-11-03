import json

with open('scripts/world_pads.json', 'r', encoding='utf-8') as f:
    wp = json.load(f)

print("LEFT 10 in world_pads.json:", wp.get('LEFT', {}).get('10'))
print("LEFT 1 in world_pads.json:", wp.get('LEFT', {}).get('1'))
print("Rasp_PI4 2 in world_pads.json:", wp.get('Rasp_PI4', {}).get('2'))
print("Rasp_PI4 39 in world_pads.json:", wp.get('Rasp_PI4', {}).get('39'))
print("Rasp_PI4 1 in world_pads.json:", wp.get('Rasp_PI4', {}).get('1'))
