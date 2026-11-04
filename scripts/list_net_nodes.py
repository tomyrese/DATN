import re

with open('project_netlist.net', 'r', encoding='utf-8') as f:
    text = f.read()

nets = re.findall(r'\(net\s+\(code\s+"\d+"\)\s+\(name\s+"([^"]+)"\)(.*?)(?=\(net\b|\)\s*\)\s*\Z)', text, re.DOTALL)

for name, body in sorted(nets, key=lambda x: x[0]):
    nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', body)
    if len(nodes) > 1:
        print(f"Net {name:25} ({len(nodes)} pins): {', '.join([f'{r}.{p}' for r, p in nodes])}")

