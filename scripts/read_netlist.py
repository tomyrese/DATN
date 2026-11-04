with open('project_netlist.net', 'r', encoding='utf-8') as f:
    text = f.read()

print("Netlist length:", len(text))
print(text[:1500])

