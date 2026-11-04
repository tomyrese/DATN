import re

with open('project_netlist.net', 'r', encoding='utf-8') as f:
    text = f.read()

comps = re.findall(r'\(comp\s+\(ref\s+"([^"]+)"\)\s+\(value\s+"([^"]+)"\)\s+\(footprint\s+"([^"]+)"\)', text)
print(f'Total components: {len(comps)}')
for ref, val, fp in comps:
    print(f'  {ref:10} {val:20} {fp}')

nets = re.findall(r'\(net\s+\(code\s+"\d+"\)\s+\(name\s+"([^"]+)"\)(.*?)(?=\(net\b|\)\s*\)\s*\Z)', text, re.DOTALL)
print(f'\nTotal nets: {len(nets)}')
for name, body in nets:
    nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', body)
    node_str = ', '.join([f'{r}.{p}' for r, p in nodes])
    print(f'  Net {name:15}: {node_str}')
