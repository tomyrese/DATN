with open('scripts/build_master_v30_pcb.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f"Total lines: {len(lines)}")
print("".join(lines[:60]))

